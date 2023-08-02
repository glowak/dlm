import re

sentence1 = 'research " extensive "'
sentence2 = 'most recently of " Who We Are:'
sentence3 = 'most recently of Who We Are "'
replaced = re.sub(r'(?<=\s)"\s*([^"]*?)\s*"(?=\s|$)', lambda match: f'"{match.group(1)}"', sentence3)
print(replaced)
replaced2 = re.sub(r'(".*?")', lambda match: match.group(0).replace(" ", ""), sentence1)
replaced3 = re.sub(r'"([^"]*?)"', lambda match: f'"{match.group(1).replace(" ", "")}"', sentence2)
print(replaced3)