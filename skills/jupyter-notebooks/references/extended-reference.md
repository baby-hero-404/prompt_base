### Delete Cell
```python
nb['cells'] = [c for c in nb['cells']
               if c.get('metadata', {}).get('id') != 'cell_to_delete']
```

---

## 📦 Common Patterns

### Setup Cell
```json
["#@title Setup\n",
 "!pip install -q package1 package2\n",
 "\n",
 "import package1\n",
 "import package2\n",
 "\n",
 "print('✓ Setup complete')\n"]
```

### Config Cell (Colab Forms)
```json
["#@title Configuration { display-mode: \"form\" }\n",
 "\n",
 "MODEL_NAME = \"gpt2\"  #@param {type:\"string\"}\n",
 "BATCH_SIZE = 32  #@param {type:\"integer\"}\n",
 "USE_GPU = True  #@param {type:\"boolean\"}\n"]
```

### Colab Form Field Syntax
```python
"#@title Cell Title { display-mode: \"form\" }\n"
"param = \"default\"  #@param {type:\"string\"}\n"
"number = 10  #@param {type:\"integer\"}\n"
"flag = True  #@param {type:\"boolean\"}\n"
"choice = \"A\"  #@param [\"A\", \"B\", \"C\"]\n"
```

### Progress Display
```json
["from tqdm.notebook import tqdm\n",
 "\n",
 "for i in tqdm(range(100)):\n",
 "    # work\n",
 "    pass\n"]
```

### Collapsible Sections (Colab)
Use `#@title` on code cells — they become collapsible when run.

---

## ✅ QUALITY CHECKLIST

Before finalizing a notebook:

- [ ] All cells have **unique IDs**
- [ ] Markdown cells have proper headers and formatting
- [ ] Code cells are **logically ordered**
- [ ] Imports are at the top or in a setup cell
- [ ] Config values use Colab form fields where appropriate
- [ ] Error handling for common failures
- [ ] Clear output messages (`✓` for success, `⚠️` for warnings)
- [ ] Section dividers between major parts
