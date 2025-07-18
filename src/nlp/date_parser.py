import dateparser
from dateparser.search import search_dates
from typing import Optional, Tuple, List, Union
import re
from datetime import datetime


class DateParser:
    def __init__(self, reference: datetime = None):
        """
        Initialize the DateParser.

        Args:
            reference (datetime, optional): Reference date for relative parsing (e.g., for testing).
        """
        self.reference = reference or datetime.now()

    def parse_single_date(self, text: str) -> Optional[str]:
        """
        Parse a single date expression and return it as ISO string.

        Args:
            text (str): Input text containing a date expression.

        Returns:
            str: ISO formatted date (e.g., '2025-07-17') or None if not found.
        """
        text = text.strip().rstrip(".,!?")
        results = search_dates(text, settings={"RELATIVE_BASE": self.reference})
        if results:
            # print(f"[DEBUG] Parsing '{text}' → {results[0][1]}")
            return results[0][1].date().isoformat()
        print(f"[DEBUG] Failed to parse '{text}'")
        return None

    def parse_date_range(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Parse a date range like 'from Monday to Friday' or 'between June 1 and June 5'.

        Args:
            text (str): Text with potential date range.

        Returns:
            Tuple[str, str]: ISO format (start_date, end_date) or None.
        """
        # Normalize phrases
        text = text.lower().strip()
        patterns = [
            r'from (.+?) to (.+?)($|[^a-z])',
            r'between (.+?) and (.+?)($|[^a-z])'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                start_text = match.group(1)
                end_text = match.group(2)
                start = dateparser.parse(start_text, settings={"RELATIVE_BASE": self.reference})
                end = dateparser.parse(end_text, settings={"RELATIVE_BASE": self.reference})
                if start and end:
                    return (start.date().isoformat(), end.date().isoformat())
        return None

    def extract_all_dates(self, text: str) -> List[str]:
        """
        Extract all dates mentioned in the text (used for fuzzy scanning).

        Args:
            text (str): Input query or message text.

        Returns:
            List[str]: All detected date strings in ISO format.
        """
        results = search_dates(text, settings={"RELATIVE_BASE": self.reference})
        return [dt[1].date().isoformat() for dt in results] if results else []

    def parse(self, text: str) -> Union[Tuple[str, str], str, None]:
        """
        Main entry point: try date range first, then fallback to single date.

        Args:
            text (str): User input text.

        Returns:
            Union[Tuple[str, str], str, None]: Range tuple, single date, or None.
        """
        range_result = self.parse_date_range(text)
        if range_result:
            return range_result
        cleaned_text = text.strip().rstrip(".,!?")
        return self.parse_single_date(cleaned_text)


# Example usage
if __name__ == "__main__":
    dp = DateParser()
    print(dp.parse("from jan 1 2025 to  today"))
    print(dp.parse(" friday"))
    print(dp.extract_all_dates("find meetings from last week and interviews next Monday"))
