import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="dateparser")

import dateparser
from dateparser.search import search_dates
from typing import Optional, Tuple, List, Union
import re
from datetime import datetime, timedelta


class DateParser:
    def __init__(self, reference: datetime = None):
        """
        Initialize the DateParser.

        Args:
            reference (datetime, optional): Reference date for relative parsing.
        """
        self.reference = reference or datetime.now()
        self.settings = {
            "RELATIVE_BASE": self.reference,
            "PREFER_DAY_OF_MONTH": "first",
        }

    def _parse_date_with_month_first(self, date_str: str) -> Optional[datetime]:
        """
        Parse a date string, ensuring month-only or month-year patterns start from the 1st.
        """
        date_str = date_str.strip()
        
        # Check if it's a month-year pattern (e.g., "jan 2025", "january 2025")
        month_year_pattern = r'^([a-zA-Z]{3,9})\s+(\d{4})$'
        match = re.match(month_year_pattern, date_str)
        if match:
            month_name = match.group(1)
            year = match.group(2)
            date_str = f"{month_name} 1, {year}"
        
        # Also handle month-only patterns (e.g., "jan", "january")
        month_only_pattern = r'^([a-zA-Z]{3,9})$'
        match = re.match(month_only_pattern, date_str)
        if match:
            month_name = match.group(1)
            year = self.reference.year
            date_str = f"{month_name} 1, {year}"
        
        return dateparser.parse(date_str, settings=self.settings)
    
    def _contains_date_keywords(self, text: str) -> bool:
        """
        Check if the text contains actual date-related keywords.
        This helps avoid false positives like "to" being parsed as a date.
        """
        text = text.lower()
    
    # Common date patterns and keywords
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY, DD/MM/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD
            r'\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',  # DD Month
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}',  # Month DD
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(today|tomorrow|yesterday)\b',
            r'\b(this|last|next)\s+(week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(before|after|since|from|until|between)\s+\d',
            r'\b(before|after|since|from|until|between)\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
            r'\b(before|after|since|from|until|between)\s+(january|february|march|april|may|june|july|august|september|october|november|december)',
            r'\bin\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
            r'\bin\s+(january|february|march|april|may|june|july|august|september|october|november|december)',
            r'\bin\s+\d{4}\b',  # in 2025
        ]
    
        for pattern in date_patterns:
            if re.search(pattern, text):
                return True
    
        return False
    
    def parse_single_date(self, text: str) -> Optional[str]:
        """
        Parse a single date expression and return it as ISO string.
        """
        text = text.strip().rstrip(".,!?")
        # print(f"[DEBUG] parse_single_date called with: {repr(text)}")
    
    # Check if the text actually contains date-related content
        if not self._contains_date_keywords(text):
            # print(f"[DEBUG] No date keywords found in: {repr(text)}")
            return None
    
        results = search_dates(text, settings=self.settings)
        # print(f"[DEBUG] search_dates returned: {results}")
    
        if results:
        # Filter out results that are just common words misinterpreted as dates
            filtered_results = []
            for date_str, dt in results:
                date_str_lower = date_str.lower()
                # Skip common words that might be misinterpreted as dates
                if date_str_lower in ['to', 'from', 'at', 'in', 'on', 'by', 'for', 'with', 'and', 'or']:
                    continue
                filtered_results.append((date_str, dt))
        
            if filtered_results:
                # print(f"[DEBUG] First filtered result: {filtered_results[0]}")
                return filtered_results[0][1].date().isoformat()
    
        return None

    def parse_date_range(self, text: str) -> Optional[Tuple[Optional[str], Optional[str]]]:
        """
        Parse a date range or open-ended range like 'since Jan 2025' or 'before May'.
        """
        text = text.lower().strip()

        # Full range: 'from X to Y' or 'between X and Y'
        # Use more specific patterns to avoid capturing too much
        patterns = [
            r'from\s+([a-zA-Z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{4}|[a-zA-Z]+)\s+to\s+([a-zA-Z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{4}|[a-zA-Z]+)',
            r'between\s+([a-zA-Z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{4}|[a-zA-Z]+)\s+and\s+([a-zA-Z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{4}|[a-zA-Z]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                start_str = match.group(1).strip()
                end_str = match.group(2).strip()
                start = self._parse_date_with_month_first(start_str)
                end = self._parse_date_with_month_first(end_str)
                if start and end:
                    return (start.date().isoformat(), end.date().isoformat())

        # Handle "in [month year]" or "in [month]" patterns - should return full month range
        in_month_pattern = re.search(r'in\s+([a-zA-Z]+\s+\d{4}|[a-zA-Z]+)', text)
        if in_month_pattern:
            month_str = in_month_pattern.group(1).strip()
            start_date = self._parse_date_with_month_first(month_str)
            if start_date:
                # Calculate the last day of the month
                if start_date.month == 12:
                    next_month = start_date.replace(year=start_date.year + 1, month=1, day=1)
                else:
                    next_month = start_date.replace(month=start_date.month + 1, day=1)
                last_day = next_month - timedelta(days=1)
                return (start_date.date().isoformat(), last_day.date().isoformat())

        # Open-ended "since" / "after"  
        since_match = re.search(r'(since|after|till)\s+', text)
        if since_match:
            remaining_text = text[since_match.end():]
            # results = search_dates(remaining_text, settings=self.settings)
            keyword = since_match.group(1)
            if keyword == "since":
            # "since" implies past dates
                relative_settings = {
                    "RELATIVE_BASE": self.reference,
                    "PREFER_DATES_FROM": "past"
                }
            elif keyword == "till" or keyword == "after":  # "after"
            # "after" could be future dates
                relative_settings = {
                "RELATIVE_BASE": self.reference,  
                "PREFER_DATES_FROM": "future"
                }
            else:
                relative_settings = self.settings

            parsed_date = dateparser.parse(remaining_text, settings=relative_settings)
            if parsed_date:
                return (parsed_date.date().isoformat(), None)
            
        # Open-ended "before"
        before_match = re.search(r'before\s+', text)  
        if before_match:
            remaining_text = text[before_match.end():]
            results = search_dates(remaining_text, settings=self.settings)
            if results:
                return (None, results[0][1].date().isoformat())
        return None

    def extract_all_dates(self, text: str) -> List[str]:
        """
        Extract all unique dates mentioned in the text.
        For range expressions, extract the actual start and end dates.
        """
        # First try to parse as a range
        range_result = self.parse_date_range(text)
        if range_result:
            dates = []
            if range_result[0]:  # start date
                dates.append(range_result[0])
            if range_result[1]:  # end date
                dates.append(range_result[1])
            return dates
        
        # If not a range, extract all individual dates
        results = search_dates(text, settings=self.settings)
        if not results:
            return []
        seen = set()
        dates = []
        for _, dt in results:
            iso = dt.date().isoformat()
            if iso not in seen:
                seen.add(iso)
                dates.append(iso)
        return dates

    def parse(self, text: str) -> Union[Tuple[Optional[str], Optional[str]], str, None]:
        """
        Main entry point: try date range first, then fallback to single date.
        """
        range_result = self.parse_date_range(text)
        if range_result:
            return range_result
        # print(f"[DEBUG] in DateParser.parse() called with: {repr(text)}")
        return self.parse_single_date(text.strip().rstrip(".,!?"))


# # # Example usage
if __name__ == "__main__":
    dp = DateParser()
    print(dp.extract_all_dates("code review metting in last 10 days"))
#     print(dp.extract_all_dates("emails from sarah to anna till next monday"))
    # print(dp.parse("emails before september 2025"))
#     print(dp.extract_all_dates("find meetings from last week and  next Monday"))

