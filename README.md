# Django Library Management System - CI/CD on AWS Elastic Beanstalk

A clean Django Library Management System structured according to the **Continuous Deployment on AWS (GitHub Actions and AWS Elastic Beanstalk)** specification, featuring:
- **Pylint** for Python & Django code quality checks.
- **SonarQube / SonarCloud** for static code analysis and test coverage reporting.
- **AWS Elastic Beanstalk** continuous deployment pipeline powered by **GitHub Actions**.

---

## 📂 Project Structure (Aligned with Document Specification)

```text
.
├── .ebextensions/
│   └── django.config              # Elastic Beanstalk WSGI & static file mapping (demoproj.wsgi:application)
├── .github/
│   └── workflows/
│       └── deploy-eb.yml          # GitHub Actions CI/CD pipeline
├── .platform/
│   └── hooks/
│       └── postdeploy/
│           └── 01_migrate.sh      # Automated post-deployment database migration & static collection
├── catalog/                       # Library Management Application
│   ├── migrations/                # Database migrations
│   ├── static/catalog/style.css   # Clean UI styling
│   ├── templates/catalog/         # HTML templates (Dashboard, Books, Members, Loans)
│   ├── admin.py                   # Django Admin registration
│   ├── forms.py                   # BookForm, MemberForm, IssueBookForm
│   ├── models.py                  # Book, Member, Loan models
│   ├── services.py                # Transactional book issue & return business logic
│   ├── tests.py                   # 28 comprehensive unit & view tests
│   ├── urls.py                    # App URL routing
│   └── views.py                   # Dashboard, CRUD & loan views
├── demoproj/                      # Main Project Package (as specified in tutorial)
│   ├── __init__.py
│   ├── asgi.py                    # ASGI interface
│   ├── settings.py                # Environment-aware settings (ALLOWED_HOSTS, STATIC_ROOT)
│   ├── urls.py                    # Root URL routing
│   └── wsgi.py                    # WSGI interface for Elastic Beanstalk
├── .gitignore                     # Git ignore rules
├── .pylintrc                      # Pylint configuration using pylint-django
├── manage.py                      # Django CLI management script
├── requirements.txt               # Production dependencies (Django LTS)
├── requirements-dev.txt           # CI/Development dependencies (Pylint, Coverage)
└── sonar-project.properties       # SonarQube / SonarCloud scanner configuration
```

---

## ⚡ Quick Execution in VS Code Terminal

When you open this folder in **VS Code**, you can directly execute commands without navigating into subfolders:

```powershell
# 1. Activate your virtual environment
.venv\Scripts\Activate.ps1

# 2. Run system checks
python manage.py check

# 3. Run all 28 automated tests
python manage.py test

# 4. Run local Pylint check
pylint --rcfile=.pylintrc catalog demoproj

# 5. Start development server
python manage.py runserver
```

---

## 🚀 AWS Elastic Beanstalk Deployment Steps

### 1. Initialize Elastic Beanstalk (EB CLI)
In the project root:
```bash
eb init -r us-east-1 -p python-3.12 gos-library-app
```

### 2. Create Single-Instance Environment (AWS Academy Learner Lab)
```bash
eb create gos-library-env \
  --single \
  --instance_type t3.micro \
  --service-role LabRole \
  --instance_profile LabInstanceProfile
```

### 3. Create S3 Deployment Bucket
```bash
aws s3 mb s3://gos-library-deploy-YOURNAME --region us-east-1
```

### 4. Configure GitHub Repository Secrets
Under your GitHub repository **Settings → Secrets and variables → Actions**, add:
- `AWS_ACCESS_KEY_ID`: From AWS Academy Learner Lab
- `AWS_SECRET_ACCESS_KEY`: From AWS Academy Learner Lab
- `AWS_SESSION_TOKEN`: From AWS Academy Learner Lab
- `EB_APPLICATION_NAME`: `gos-library-app`
- `EB_ENVIRONMENT_NAME`: `gos-library-env`
- `EB_S3_BUCKET`: `gos-library-deploy-YOURNAME`
- `SONAR_TOKEN`: Token from SonarCloud or SonarQube
- `SONAR_HOST_URL`: `https://sonarcloud.io` (or your SonarQube host)

### 5. Push to GitHub
```bash
git init -b main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git add .
git commit -m "feat: initial commit ready for Elastic Beanstalk CI/CD"
git push -u origin main
```
