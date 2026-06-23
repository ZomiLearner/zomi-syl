# ⭐ **Section: Adding New Models (Backends)**

## **🧩 Adding New Models (Backends)**

`zomi-syl` is designed to support multiple syllabification backends through a unified registry.  
New models can be added without modifying the core engine by following the backend template and metadata schema.

### **Backend Types Supported**
- Rule‑based backends  
- CRF / statistical backends  
- Transformer / neural backends  
- FST‑based backends  
- Hybrid backends  

### **Backend Architecture Overview**
All backends live under:

```
src/zomi_syl/backends/
```

Each backend must implement:

- a **Backend class**  
- a **predict()** method  
- a **load()** method  
- a **metadata.json** file (Unified Metadata Schema v1.0)  
- optional model files (e.g., `.joblib`, `.json`, `.bin`)  

Backends are registered automatically through:

```
src/zomi_syl/registry/models.py
```

### **Steps to Implement a New Backend**

1. **Create a backend folder**

```
src/zomi_syl/backends/my_backend/
```

2. **Add backend implementation**

```
my_backend_backend.py
```

3. **Add metadata**

```
metadata.json
```

4. **Add model files (if needed)**  
Place them under:

```
src/zomi_syl/models/my_backend/
```

5. **Register the backend**  
Add an entry in:

```
src/zomi_syl/registry/models.py
```

6. **Add tests**  
Use the template:

```
tests/backends/template_test_my_backend.py
```

7. **Document the backend**  
Follow:

- **New Backend Template**  
- **Developer Guide for Adding New Backends**  
- **Unified Metadata Schema**  

### **Testing Your Backend**

Run backend tests:

```
pytest tests/backends/test_my_backend.py
```

Run CLI tests:

```
pytest tests/cli/test_cli_commands.py
```

Run integration tests:

```
pytest tests/integration/test_syllabify_integration.py
```

### **Benchmark Your Backend**

```
zomi-syl models benchmark my_backend
```

Compare with others:

```
zomi-syl models compare rule crf my_backend
```

### **Backend Development Resources**

- **Backend Loader**  
- **Unified Metadata Schema**  
- **Template Test Backend**  
- **Recommended Folder Structure**  

---
