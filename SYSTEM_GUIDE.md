# 📚 Fisheries System - Complete Guide

## 🗂️ File Structure & Locations

### **🏗️ BACKEND FILES (Python)**

| File | Purpose | Key Functions |
|------|---------|---------------|
| **app.py** | Main Flask application | All routes, authentication, APIs |
| **face_models.py** | Database models | User, FaceData, Attendance tables |  
| **face_recognition_core.py** | Face algorithms | Face detection, encoding, comparison |
| **redis_config.py** | Redis operations | Caching, counters, data storage |

### **🎨 FRONTEND FILES (HTML)**

| Template | Purpose | Route |
|----------|---------|-------|
| **base.html** | Base template (navbar, CSS) | Extended by all pages |
| **login.html** | Username/password login | `/login` |
| **face_login.html** | Face recognition login | `/face/login` |
| **welcome.html** | Home page after login | `/welcome` |
| **dashboard_budidaya.html** | Budidaya dashboard | `/dashboard/budidaya` |
| **dashboard_tangkap.html** | Tangkap dashboard | `/dashboard/tangkap` |
| **dashboard_pdspkp.html** | Sertifikasi dashboard | `/dashboard/pdspkp` |
| **face_enrollment.html** | Face registration | `/face/enrollment` |

---

# 🔍 COMPONENT LOCATIONS

## 🏠 HOME PAGE (Welcome)

**📁 File**: `templates/welcome.html`
**🔗 Route**: `/welcome` di `app.py` line 70

```python
@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html')
```

**🔧 Cara Tambah Content**:
```python
# Di app.py:
@app.route('/welcome')
def welcome():
    extra_data = {
        'login_count': redis_manager.get_data(f"login_count:{session['username']}"),
        'notifications': ['System update', 'New features']
    }
    return render_template('welcome.html', data=extra_data)

# Di welcome.html:
<p>Login Count: {{ data.login_count }}</p>
```

## 📊 DASHBOARD SYSTEM

### **🌱 Dashboard Budidaya**
**📁 File**: `templates/dashboard_budidaya.html` + `app.py` line 97

```python
@app.route('/dashboard/budidaya')
@require_role('budidaya')  # Hanya user budidaya bisa akses
def dashboard_budidaya():
    stats = {
        'total_kolam': 125,
        'produksi_bulan': 2.5
    }
    return render_template('dashboard_budidaya.html', stats=stats)
```

**🔧 Cara Tambah Feature**:
```python
# 1. Update function:
def dashboard_budidaya():
    new_data = {
        'kolam_list': get_kolam_data(),  # NEW
        'weather': get_weather_data()    # NEW
    }
    return render_template('dashboard_budidaya.html', stats=new_data)

# 2. Helper function:
def get_kolam_data():
    return [{'id': 'KLM001', 'jenis': 'Lele', 'stok': 5000}]

# 3. Display di template:
{% for kolam in stats.kolam_list %}
    <tr><td>{{ kolam.id }}</td><td>{{ kolam.jenis }}</td></tr>
{% endfor %}
```

## 🔐 LOGIN SYSTEM

### **👤 Traditional Login** 
**📁 File**: `templates/login.html` + `app.py` line 41

**👥 User Data** (app.py line 33):
```python
demo_users = {
    'user_budidaya': {'password': 'passwordbud', 'role': 'budidaya'},
    'user_tangkap': {'password': 'passwordtang', 'role': 'tangkap'},
    'user_pds': {'password': 'passwordpds', 'role': 'pdspkp'}
}
```

**🔧 Cara Tambah User**:
```python
demo_users = {
    'user_budidaya': {'password': 'passwordbud', 'role': 'budidaya'},
    'user_tangkap': {'password': 'passwordtang', 'role': 'tangkap'},
    'user_pds': {'password': 'passwordpds', 'role': 'pdspkp'},
    'admin': {'password': 'admin123', 'role': 'admin'}  # NEW
}
```

### **🎭 Face Recognition Login**
**📁 File**: `templates/face_login.html` + `app.py` line 240

**📡 API**: `/api/recognize-face` (POST) - Process face recognition

---

# 🔧 HOW TO ADD NEW FUNCTIONS

## 🆕 1. ADD NEW PAGE

```python
# Step 1: Add route di app.py (end of file)
@app.route('/new-feature')
def new_feature():
    data = {'title': 'New Feature'}
    return render_template('new_feature.html', data=data)

# Step 2: Create templates/new_feature.html
{% extends "base.html" %}
{% block content %}
    <h2>{{ data.title }}</h2>
{% endblock %}

# Step 3: Add navigation di base.html
<a href="{{ url_for('new_feature') }}" class="nav-link">New Feature</a>
```

## 📡 2. ADD NEW API

```python
# Add di app.py:
@app.route('/api/new-endpoint', methods=['POST'])
def api_new_endpoint():
    data = request.get_json()
    result = {'success': True, 'data': process_data(data)}
    return jsonify(result)

# Call dari JavaScript:
fetch('/api/new-endpoint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({key: 'value'})
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🗄️ 3. ADD DATABASE OPERATIONS

```python
# Add model di face_models.py:
class NewTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Use di app.py:
new_record = NewTable(name='test')
db.session.add(new_record)
db.session.commit()

# Query:
records = NewTable.query.all()
```

## 🔄 4. ADD REDIS OPERATIONS

```python
# Save data:
redis_manager.set_data('key', {'data': 'value'}, expire_time=3600)

# Get data:  
data = redis_manager.get_data('key')

# Counter:
redis_manager.increment_counter('page_views')
```

---

# 🚀 DEVELOPMENT WORKFLOW

## **📝 Adding New Features**

### **1. Planning**
- Define what feature does
- Identify files to modify
- Plan database changes

### **2. Backend (app.py)**
```python
# Add route
@app.route('/feature-route')
def feature_function():
    return render_template('feature_template.html')

# Add API if needed
@app.route('/api/feature-api', methods=['POST']) 
def api_feature():
    return jsonify({'result': 'success'})
```

### **3. Frontend (templates/)**
```html
<!-- Create feature_template.html -->
{% extends "base.html" %}
{% block content %}
    <!-- Feature HTML here -->
{% endblock %}
```

### **4. Test Local**
```bash
python app.py
# Test new feature di browser
```

### **5. Deploy**
```bash
git add .
git commit -m "Add new feature"
git push
# Railway auto-deploys
```

---

# 📱 CURRENT SYSTEM FEATURES

## **✅ Implemented Features**

1. **🔐 Multi-Login System**: Username/password + face recognition
2. **📊 Role-Based Dashboards**: Budidaya, Tangkap, Sertifikasi  
3. **📸 Face Recognition**: Enrollment + login + attendance
4. **🔄 Redis Integration**: Caching, statistics, session tracking
5. **🗄️ Database System**: User, face data, attendance tracking
6. **📱 Responsive Design**: Mobile-friendly interface
7. **☁️ Cloud Deployment**: Railway integration

## **🎯 How Each Works**

### **Login Flow**:
```
1. User access /login atau /face/login
2. Authentication (password atau face)
3. Set session variables (user_id, role)  
4. Redirect ke /welcome (home)
5. From welcome, access role-specific dashboard
```

### **Face Recognition Flow**:
```
1. Face enrollment: /face/enrollment → capture → save encoding
2. Face login: /face/login → capture → compare → authenticate
3. Database: face encodings stored as JSON in FaceData table
4. Redis: track statistics (login counts, confidence scores)
```

### **Dashboard Access**:
```
1. /dashboard route checks user role
2. Redirect ke dashboard sesuai role:
   - budidaya → /dashboard/budidaya  
   - tangkap → /dashboard/tangkap
   - pdspkp → /dashboard/pdspkp
3. @require_role decorator protects access
```

---

# 🔒 SECURITY SYSTEM

## **🛡️ Role Protection**
```python
# @require_role decorator (app.py line 24):
@require_role('budidaya')  # Only budidaya users
def dashboard_budidaya():
    return render_template('dashboard_budidaya.html')

# Multi-role access:
@require_roles('admin', 'manager')  # Custom decorator
def admin_manager_page():
    return render_template('admin_page.html')
```

## **🔍 Session Management**
```python
# Session variables set saat login:
session['user_id'] = username      # User identifier
session['username'] = username     # Display name
session['role'] = user_role        # Access control
session['login_method'] = 'face'   # Track login type
```

---

# 🎉 READY FOR DEVELOPMENT

**🎯 You now understand:**
- ✅ Where each component is located
- ✅ How authentication system works
- ✅ How to add new pages/features
- ✅ How database and Redis integration works
- ✅ How to deploy updates to Railway

**🚀 Next Steps:**
1. Test current system locally
2. Add your custom features
3. Push to Railway for live deployment

**📞 Need help? Each function has detailed comments explaining purpose and usage!**
