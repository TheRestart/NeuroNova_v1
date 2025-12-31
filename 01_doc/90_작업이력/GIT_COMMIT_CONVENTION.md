# Git 커밋 메시지 규칙 (Commit Convention)

**목적**: 일관성 있는 Git 커밋 히스토리 유지
**적용 범위**: NeuroNova CDSS 전체 저장소
**최종 수정일**: 2025-12-31

---

## 📋 기본 형식

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 예시
```
feat(UC02): Add patient registration API

- Implement POST /api/emr/patients/ endpoint
- Add PatientSerializer with validation
- Integrate with OpenEMR sync

Closes #12
```

---

## 🏷️ Type (필수)

커밋의 성격을 나타내는 접두사:

| Type | 설명 | 예시 |
|------|------|------|
| **feat** | 새로운 기능 추가 | `feat(UC03): Add prescription order API` |
| **fix** | 버그 수정 | `fix(auth): Resolve login authentication error` |
| **docs** | 문서 수정 (코드 변경 없음) | `docs: Update README with DICOM setup` |
| **refactor** | 코드 리팩토링 (기능 변화 없음) | `refactor(emr): Simplify patient query logic` |
| **test** | 테스트 추가/수정 | `test(ocs): Add integration tests for order flow` |
| **chore** | 빌드/설정 파일 수정 | `chore: Update dependencies (Django 4.2.9)` |
| **style** | 코드 포맷팅 (세미콜론, 공백 등) | `style: Apply Black formatter to models.py` |
| **perf** | 성능 개선 | `perf(db): Add index to Patient.ssn field` |
| **ci** | CI/CD 설정 수정 | `ci: Add GitHub Actions workflow` |
| **revert** | 이전 커밋 되돌리기 | `revert: Revert "feat(UC06): Add AI model"` |

---

## 🎯 Scope (선택사항)

변경 범위를 명시:

### Use Case별
- `UC01`, `UC02`, `UC03`, ... `UC09`
- 예: `feat(UC05): Add RIS DICOM upload`

### 모듈별
- `auth`, `emr`, `ocs`, `lis`, `ris`, `ai`, `alert`, `audit`, `fhir`
- 예: `fix(auth): Resolve JWT token expiration`

### 인프라별
- `docker`, `nginx`, `ci`, `deploy`
- 예: `chore(docker): Update Orthanc to v1.12.0`

### 문서별
- `docs`, `readme`, `api-spec`
- 예: `docs(api-spec): Add Swagger annotations for UC03`

---

## 📝 Subject (필수)

### 규칙
1. **동사 원형**으로 시작 (현재형, 명령형)
   - ✅ `Add patient API`
   - ❌ `Added patient API`
   - ❌ `Adding patient API`

2. **첫 글자 대문자**
   - ✅ `Add patient API`
   - ❌ `add patient API`

3. **마침표 없음**
   - ✅ `Fix login bug`
   - ❌ `Fix login bug.`

4. **50자 이내** 권장
   - ✅ `Add patient registration with OpenEMR sync`
   - ❌ `Add patient registration functionality with automatic synchronization to OpenEMR external system`

### 자주 사용하는 동사
- Add, Remove, Update, Fix, Implement
- Refactor, Optimize, Improve, Enhance
- Rename, Move, Merge, Split

---

## 📄 Body (선택사항)

### 언제 작성?
- 변경 사항이 복잡하거나 여러 파일에 걸쳐있을 때
- "무엇을", "왜" 변경했는지 설명 필요할 때

### 규칙
1. **Subject와 한 줄 공백** 후 작성
2. **72자마다 줄바꿈**
3. **불렛 포인트** 사용 권장 (`-`, `*`)

### 예시
```
feat(UC06): Add AI model integration

- Implement Celery task for asynchronous AI inference
- Add FastAPI endpoint for model prediction
- Integrate with Orthanc DICOM retrieval
- Store results in AIJobResult model

This change enables doctors to request AI analysis
on DICOM images and receive notifications when complete.
```

---

## 🔗 Footer (선택사항)

### Issue 참조
```
Closes #123
Fixes #456
Resolves #789
```

### Breaking Changes (중요)
```
BREAKING CHANGE: JWT token expiration changed from 24h to 1h

All clients must refresh tokens every hour instead of daily.
Update mobile app to handle 401 errors gracefully.
```

### Co-authored-by
```
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## ✅ 좋은 예시

### 예시 1: 기능 추가
```
feat(UC03): Add medication prescription API

- Implement POST /api/ocs/prescriptions/ endpoint
- Add PrescriptionSerializer with drug code validation
- Integrate with pharmacy system via FHIR
- Add unit tests for prescription workflow

Closes #34
```

### 예시 2: 버그 수정
```
fix(auth): Resolve password hashing in create_test_users

Fixed bug where password parameter was not passed to
create_user(), causing authentication failures.

- Remove password from user_data.pop()
- Pass password explicitly to create_user()
- Change special chars to simple format (admin123)

Fixes #8
```

### 예시 3: 문서 업데이트
```
docs: Update password change plan

- Move PASSWORD_CHANGE_PLAN.md to 01_doc/90_작업이력/
- Update all docs with new password format (*123)
- Add DICOM sample data download guide
```

### 예시 4: 리팩토링
```
refactor(emr): Simplify patient query with select_related

Optimized N+1 query problem in PatientViewSet by adding
select_related('encounter__doctor') to queryset.

Performance improvement: 15 queries → 2 queries
```

### 예시 5: 설정 변경
```
chore(docker): Add Prometheus monitoring stack

- Add prometheus, grafana, alertmanager to docker-compose
- Configure alert rules for CODE BLUE, CRITICAL, WARNING
- Add Grafana dashboard for system metrics

Refs #45
```

---

## ❌ 나쁜 예시

### 예시 1: 모호한 Subject
```
❌ fix: bug fix
❌ update: change
❌ 클로드1
❌ 00
```

**개선**:
```
✅ fix(auth): Resolve login authentication error
✅ feat(UC05): Add DICOM upload functionality
```

### 예시 2: Type 누락
```
❌ Add patient API
❌ Fixed login bug
```

**개선**:
```
✅ feat(UC02): Add patient API
✅ fix(auth): Resolve login bug
```

### 예시 3: Subject가 너무 김
```
❌ feat: Add patient registration functionality with automatic synchronization to OpenEMR external system and FHIR resource generation
```

**개선**:
```
✅ feat(UC02): Add patient registration with OpenEMR sync

- Implement POST /api/emr/patients/ endpoint
- Auto-sync to OpenEMR and generate FHIR resources
```

---

## 🔄 Git Workflow (권장)

### 브랜치 명명 규칙
```
<type>/<issue-number>-<short-description>

예시:
feature/34-prescription-api
fix/8-login-authentication
docs/update-readme
hotfix/critical-security-bug
```

### 커밋 흐름
```bash
# 1. 브랜치 생성
git checkout -b feature/34-prescription-api

# 2. 작업 및 커밋
git add .
git commit -m "feat(UC03): Add prescription API endpoint"

# 3. 추가 커밋
git commit -m "test(UC03): Add prescription unit tests"
git commit -m "docs(UC03): Update API spec with prescription"

# 4. Push 및 PR 생성
git push origin feature/34-prescription-api
# GitHub에서 Pull Request 생성
```

---

## 🛠️ 도구 및 자동화

### 1. Commitlint (권장)
```bash
# 설치
npm install --save-dev @commitlint/cli @commitlint/config-conventional

# .commitlintrc.json 생성
{
  "extends": ["@commitlint/config-conventional"]
}

# Husky pre-commit hook
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

### 2. Commitizen (Interactive CLI)
```bash
# 설치
npm install --save-dev commitizen

# 사용
npx cz
# Interactive prompt로 커밋 메시지 작성
```

### 3. Conventional Changelog
```bash
# 설치
npm install --save-dev conventional-changelog-cli

# CHANGELOG.md 자동 생성
npx conventional-changelog -p angular -i CHANGELOG.md -s
```

---

## 📊 커밋 통계 (참고)

### 이상적인 커밋 빈도
- **1개 기능 = 1개 커밋** (가능하면)
- **하루 평균 3-5개 커밋** (개발 중)
- **너무 작은 커밋** (typo 수정 등)은 squash

### 커밋 크기
- **Small**: 10-50 lines (권장)
- **Medium**: 50-200 lines
- **Large**: 200+ lines (분할 권장)

---

## 🚨 특별한 경우

### Merge Commit
```
Merge branch 'feature/34-prescription-api' into develop

Resolves #34
```

### Revert Commit
```
revert: Revert "feat(UC06): Add AI model integration"

This reverts commit abc123def456.

Reason: AI model accuracy below 80% threshold.
Will be re-implemented after model retraining.
```

### Initial Commit
```
chore: Initial commit

- Setup Django project structure
- Add docker-compose for infrastructure
- Configure CI/CD pipeline
```

---

## 📚 참고 자료

- **Conventional Commits**: https://www.conventionalcommits.org/
- **Angular Convention**: https://github.com/angular/angular/blob/main/CONTRIBUTING.md
- **Semantic Versioning**: https://semver.org/

---

**작성**: Claude AI
**최종 업데이트**: 2025-12-31
**버전**: 1.0
