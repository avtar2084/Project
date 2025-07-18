import re
from typing import List
from typing import List, Set, Callable

class BooleanParser:
    def __init__(self):
        self.operators = {'AND': 2, 'OR': 1, 'NOT': 3}

    def tokenize(self, query: str) -> List[str]:
        query = query.replace("(", " ( ").replace(")", " ) ")
        return query.upper().split()

    def to_postfix(self, tokens: List[str]) -> List[str]:
        output = []
        stack = []

        def precedence(op):
            return self.operators.get(op, 0)

        for token in tokens:
            if token in ('AND', 'OR', 'NOT'):
                while (stack and stack[-1] != '(' and
                       precedence(stack[-1]) >= precedence(token)):
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            else:
                output.append(token.lower())

        while stack:
            output.append(stack.pop())

        return output

    def parse(self, query: str) -> List[str]:
        tokens = self.tokenize(query)
        return self.to_postfix(tokens)

    def evaluate(self, postfix: List[str], match_fn: Callable[[str], Set[int]]) -> Set[int]:
        stack = []
        for token in postfix:
            if token.upper() == "AND":
                b = stack.pop()
                a = stack.pop()
                stack.append(a & b)
            elif token.upper() == "OR":
                b = stack.pop()
                a = stack.pop()
                stack.append(a | b)
            elif token.upper() == "NOT":
                a = stack.pop()
                all_items = match_fn("__ALL__")
                stack.append(all_items - a)
            else:
                stack.append(match_fn(token))

        return stack[0] if stack else set()

# if __name__ == "__main__":
#     parser = BooleanParser()
    
#     q1 = "emails from Alice and (onboarding or interviews)"
#     print(parser.parse(q1))
#     # Output: ['emails', 'from', 'alice', 'onboarding', 'interviews', 'OR', 'AND']



if __name__ == "__main__":
    parser = BooleanParser()

    # Fake match function — returns dataset indexes
    dataset = [
        {"from": "alice", "topic": "onboarding"},
        {"from": "bob", "topic": "interviews"},
        {"from": "carol", "topic": "onboarding"},
    ]

    def match_fn(term: str) -> Set[int]:
        if term == "__ALL__":
            return set(range(len(dataset)))
        return {
            i for i, item in enumerate(dataset)
            if term in str(item.get("from", "")) or term in str(item.get("topic", ""))
        }

    postfix = parser.parse("alice or (bob and onboarding)")
    print("Postfix:", postfix)

    result = parser.evaluate(postfix, match_fn)
    print("Matched indices:", result)
