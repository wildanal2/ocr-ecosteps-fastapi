# OCR Regex Quick Reference

## 🎯 Pattern Cheat Sheet

### Apple Health
```python
# Priority 1: Indonesian format
r'(\d{1,2}[.,]\d{3})\s*langkah'          # 15.076 langkah

# Priority 2: TOTAL keyword
r'(?:TOTAL|Total)\s+(\d{1,2}[.,]\d{3})\s*steps'  # TOTAL 12.515 steps

# Priority 3: Today keyword
r'Today\s+(?:Today\s+)?(\d{1,2}[.,]\d{3})'       # Today 10.818

# Priority 4: No space
r'(\d{3,5})steps'                        # 401steps

# Priority 5: Large numbers
r'\b(\d{5})\b'                           # 20696
```

### Google Fit
```python
# Priority 1: Heart Points
r'(\d{1,2}[.,]?\d{3})\s*(?:Poin Kardio|Heart Pts|CHeart Pts)'  # 2.741 Poin Kardio

# Priority 2: Langkah/Steps
r'(?:Langkah|Steps)\s+(\d{1,2}[.,]\d{3})'  # Langkah 16.828
```

### Huawei Health
```python
# Priority 1: Before slash
r'(\d{1,5})\s*/\s*\d+[.,]?\d*\s*steps'   # 824 /10.000 steps

# Priority 2: After Steps
r'Steps.*?(\d{1,2}[.,]\d{3})'            # Steps ... 8.376

# Priority 3: Standard
r'(\d{1,2}[.,]\d{3})\s*steps'            # 5.117 steps
```

### Samsung Health
```python
# Priority 1: Not after slash
r'(?<!/)(\d{1,2}[.,]\d{3})\s*steps'      # 12.838 steps

# Priority 2: Indonesian
r'(\d{1,2}[.,]\d{3})\s*langkah'          # 2.304 langkah

# Priority 3: Small numbers
r'\b(\d{2,3})\b.*steps'                  # 77 steps

# Priority 4: Large numbers
r'\b(\d{5})\b'                           # 25235
```

### Fitbit
```python
# Priority 1: Today keyword
r'Today\s+(\d{1,2}[.,]\d{3})\s*Steps'    # Today 11.820 Steps

# Priority 2: Standard
r'(\d{1,2}[.,]\d{3})\s*steps'            # 10.365 steps

# Priority 3: 4-digit
r'(\d{4})\s*steps'                       # 3735 steps
```

## 🔧 Helper Functions

### Number Normalization
```python
def normalize_number(num_str: str) -> int:
    return int(num_str.replace('.', '').replace(',', '').replace(' ', ''))

# Examples:
normalize_number("15.076")  # → 15076
normalize_number("15,076")  # → 15076
normalize_number("15 076")  # → 15076
```

### App Classification
```python
def classify_app(text: str) -> str:
    text_lower = text.lower()
    
    if 'heart pts' in text_lower or 'poin kardio' in text_lower:
        return 'Google Fit'
    elif 'huawei' in text_lower or 'health+' in text_lower:
        return 'Huawei Health'
    elif 'samsung health' in text_lower or 'together' in text_lower:
        return 'Samsung Health'
    elif 'fitbit' in text_lower:
        return 'Fitbit'
    elif 'activity' in text_lower or 'summary' in text_lower:
        return 'Apple Health'
    return 'Other'
```

## 📊 Test Cases

### Apple Health
| Input | Pattern | Output |
|-------|---------|--------|
| "15.076 langkah" | Pattern 1 | 15076 |
| "TOTAL 12.515 steps" | Pattern 2 | 12515 |
| "Today 10.818" | Pattern 3 | 10818 |
| "401steps" | Pattern 4 | 401 |
| "20696" | Pattern 5 | 20696 |

### Google Fit
| Input | Pattern | Output |
|-------|---------|--------|
| "2.741 Poin Kardio" | Pattern 1 | 2741 |
| "827 CHeart Pts" | Pattern 1 | 827 |

### Huawei Health
| Input | Pattern | Output |
|-------|---------|--------|
| "824 /10.000 steps" | Pattern 1 | 824 |
| "Steps ... 8.376" | Pattern 2 | 8376 |
| "5.117 steps" | Pattern 3 | 5117 |

### Samsung Health
| Input | Pattern | Output |
|-------|---------|--------|
| "12.838 steps" | Pattern 1 | 12838 |
| "2.304 langkah" | Pattern 2 | 2304 |
| "77 steps" | Pattern 3 | 77 |
| "25235" | Pattern 4 | 25235 |

### Fitbit
| Input | Pattern | Output |
|-------|---------|--------|
| "Today 11.820 Steps" | Pattern 1 | 11820 |
| "10.365 steps" | Pattern 2 | 10365 |
| "3735 steps" | Pattern 3 | 3735 |

## 🚀 Usage Example

```python
import re

def extract_steps_example(text: str, app: str) -> int:
    if app == 'Apple Health':
        # Try patterns in order
        patterns = [
            r'(\d{1,2}[.,]\d{3})\s*langkah',
            r'(?:TOTAL|Total)\s+(\d{1,2}[.,]\d{3})\s*steps',
            r'Today\s+(?:Today\s+)?(\d{1,2}[.,]\d{3})',
            r'(\d{3,5})steps',
            r'\b(\d{5})\b'
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.I)
            if m:
                return normalize_number(m.group(1))
    
    return None

# Test
text = "Summary Today 15.076 langkah"
steps = extract_steps_example(text, 'Apple Health')
print(steps)  # → 15076
```

## 🎨 Regex Flags

```python
re.I          # Case insensitive
re.DOTALL     # . matches newline
re.MULTILINE  # ^ and $ match line boundaries
```

## 💡 Tips

1. **Always normalize numbers** after extraction
2. **Use priority order** - most specific patterns first
3. **Test with real OCR output** - includes typos
4. **Handle edge cases** - small numbers, large numbers, no separators
5. **Consider context** - keywords around numbers matter

## 🔍 Debugging

```python
import re

text = "Your OCR text here"
pattern = r'(\d{1,2}[.,]\d{3})\s*langkah'

# Test pattern
match = re.search(pattern, text, re.I)
if match:
    print(f"Found: {match.group(1)}")
    print(f"Position: {match.span()}")
else:
    print("No match")

# Find all matches
matches = re.findall(pattern, text, re.I)
print(f"All matches: {matches}")
```

## 📚 Resources

- [Python re documentation](https://docs.python.org/3/library/re.html)
- [Regex101 - Online tester](https://regex101.com/)
- [RegExr - Visual tester](https://regexr.com/)

---

**Version:** 2.0  
**Last Updated:** 2025-01-06
