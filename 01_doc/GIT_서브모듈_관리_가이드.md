# Git 서브모듈 관리 가이드

**작성일**: 2025-12-31
**버전**: 1.0
**목적**: NeuroNova 프로젝트의 Git 서브모듈 구조 이해 및 관리 방법

---

## 📚 Git 서브모듈이란?

**Git 서브모듈(Submodule)**은 Git 저장소(Repository) 안에 또 다른 Git 저장소를 폴더처럼 넣어서 관리하는 기능입니다.

### 핵심 개념

```
메인 저장소 (NeuroNova_v1)
├── .git/                    ← 메인 저장소의 Git 데이터
├── .gitmodules              ← 서브모듈 설정 파일
├── 01_doc/
├── NeuroNova_02_back_end/
└── NeuroNova_03_front_end_react/  ← 서브모듈 (독립적인 Git 저장소)
    └── .git/                ← 서브모듈의 Git 데이터
```

### 왜 서브모듈을 사용하나?

1. **독립적인 버전 관리**: 프론트엔드와 백엔드를 각각 별도의 Git 저장소로 관리
2. **팀 협업**: 프론트엔드 팀과 백엔드 팀이 독립적으로 작업 가능
3. **재사용성**: 다른 프로젝트에서도 서브모듈을 재사용 가능
4. **커밋 이력 분리**: 각 저장소의 커밋 이력이 독립적으로 관리됨

---

## 🏗️ NeuroNova 프로젝트 구조

### 저장소 구성

| 저장소 | 타입 | 역할 | GitHub URL |
|--------|------|------|------------|
| **NeuroNova_v1** | 메인 저장소 | 전체 프로젝트 통합 관리 | (메인 저장소 URL) |
| **NeuroNova_03_front_end_react** | 서브모듈 | React 프론트엔드 | https://github.com/TheRestart/NeuroNova_03_front_end_react.git |

### .gitmodules 파일

메인 저장소 루트의 `.gitmodules` 파일에 서브모듈 정보가 기록됩니다:

```ini
[submodule "NeuroNova_03_front_end_react"]
	path = NeuroNova_03_front_end_react
	url = https://github.com/TheRestart/NeuroNova_03_front_end_react.git
```

**필드 설명**:
- `path`: 메인 저장소 내 서브모듈의 위치
- `url`: 서브모듈의 원격 저장소 주소

---

## 🔧 서브모듈 작업 방법

### 1. 서브모듈 초기화 (Clone 후 최초 1회)

메인 저장소를 클론한 후, 서브모듈을 초기화해야 합니다:

```bash
# 메인 저장소 클론
git clone <NeuroNova_v1_URL>
cd NeuroNova_v1

# 서브모듈 초기화 및 업데이트
git submodule init
git submodule update
```

또는 클론 시 한 번에 서브모듈을 받을 수 있습니다:

```bash
# --recurse-submodules 옵션으로 서브모듈까지 함께 클론
git clone --recurse-submodules <NeuroNova_v1_URL>
```

---

### 2. 서브모듈에서 작업하기

#### 프론트엔드 코드 수정

```bash
# 서브모듈 디렉토리로 이동
cd NeuroNova_03_front_end_react

# 현재 브랜치 확인 (일반적으로 detached HEAD 상태)
git status

# 작업용 브랜치로 체크아웃
git checkout main

# 코드 수정 후 커밋
git add .
git commit -m "feat: Add new feature"

# 서브모듈 원격 저장소에 푸시
git push origin main
```

#### 메인 저장소로 돌아와 서브모듈 참조 업데이트

```bash
# 메인 저장소 루트로 이동
cd ..

# 메인 저장소에서 서브모듈의 새 커밋 기록
git add NeuroNova_03_front_end_react
git commit -m "chore: Update frontend submodule reference"
git push origin main
```

---

### 3. 서브모듈 최신 상태로 업데이트

다른 팀원이 서브모듈을 업데이트한 경우:

```bash
# 메인 저장소 pull
git pull

# 서브모듈도 최신 상태로 업데이트
git submodule update --remote
```

---

### 4. VSCode에서 서브모듈 작업

#### 문제 상황
VSCode에서 메인 저장소를 열면, 서브모듈이 "modified content, untracked content"로 표시되는 경우가 있습니다.

#### 해결 방법

**방법 1: 별도 VSCode 창 열기 (권장)**
```bash
# 서브모듈 디렉토리를 별도 VSCode 창으로 열기
code NeuroNova_03_front_end_react
```

**방법 2: VSCode 설정 변경**

`.vscode/settings.json`에 추가:
```json
{
  "git.detectSubmodules": true,
  "git.decorations.enabled": true
}
```

---

## 📝 자주 사용하는 명령어

### 서브모듈 상태 확인

```bash
# 서브모듈 목록 및 현재 커밋 확인
git submodule status

# 서브모듈의 변경 사항 확인
git diff --submodule
```

### 서브모듈 업데이트

```bash
# 모든 서브모듈을 최신 커밋으로 업데이트
git submodule update --remote

# 특정 서브모듈만 업데이트
git submodule update --remote NeuroNova_03_front_end_react
```

### 서브모듈 추가 (이미 완료됨)

```bash
# 새 서브모듈 추가 (참고용)
git submodule add <repository-url> <path>

# 예시:
git submodule add https://github.com/TheRestart/NeuroNova_03_front_end_react.git NeuroNova_03_front_end_react
```

### 서브모듈 제거 (필요 시)

```bash
# 1. .gitmodules에서 해당 섹션 삭제
# 2. .git/config에서 해당 섹션 삭제
# 3. 캐시 제거 및 디렉토리 삭제
git rm --cached NeuroNova_03_front_end_react
rm -rf NeuroNova_03_front_end_react
git commit -m "Remove frontend submodule"
```

---

## 🚨 주의사항

### 1. Detached HEAD 상태

서브모듈은 기본적으로 특정 커밋을 가리키므로, **detached HEAD** 상태입니다.

```bash
# 서브모듈에서 작업 전 반드시 브랜치 체크아웃
cd NeuroNova_03_front_end_react
git checkout main  # 또는 작업할 브랜치
```

### 2. 서브모듈 커밋 순서

올바른 순서:
1. **서브모듈에서 커밋 & 푸시**
2. **메인 저장소에서 서브모듈 참조 업데이트 커밋 & 푸시**

잘못된 순서:
- 메인 저장소만 푸시하면 서브모듈 커밋이 누락됨
- 서브모듈 푸시 없이 메인 저장소만 업데이트하면 다른 팀원이 해당 커밋을 받을 수 없음

### 3. .gitignore 충돌

메인 저장소의 `.gitignore`가 서브모듈 내 파일에 영향을 주지 않도록 주의합니다.

---

## 🔄 작업 흐름 예시

### 시나리오: 프론트엔드에 새 기능 추가

#### 1단계: 서브모듈에서 작업

```bash
# 서브모듈로 이동
cd NeuroNova_03_front_end_react

# 작업 브랜치로 전환
git checkout main
git pull origin main

# 코드 수정 (예: OHIF Viewer 통합)
# ... 파일 수정 ...

# 커밋 및 푸시
git add .
git commit -m "feat: Integrate OHIF Viewer as npm package"
git push origin main
```

#### 2단계: 메인 저장소에서 참조 업데이트

```bash
# 메인 저장소로 복귀
cd ..

# 서브모듈 변경 사항 확인
git status
# 출력: modified:   NeuroNova_03_front_end_react (new commits)

# 서브모듈 참조 업데이트
git add NeuroNova_03_front_end_react
git commit -m "chore: Update frontend submodule to include OHIF integration"
git push origin main
```

#### 3단계: 다른 개발자가 업데이트 받기

```bash
# 메인 저장소 pull
git pull

# 서브모듈도 업데이트
git submodule update --init --recursive
```

---

## 📊 NeuroNova 프로젝트 Git 전략

### 커밋 전략

| 저장소 | 커밋 주기 | 커밋 메시지 형식 |
|--------|-----------|-----------------|
| **Frontend (서브모듈)** | 기능 단위 | `feat:`, `fix:`, `style:`, `refactor:` |
| **Backend (메인 저장소)** | 기능 단위 | `feat:`, `fix:`, `docs:`, `test:` |
| **Main (서브모듈 참조)** | 서브모듈 업데이트 시 | `chore: Update frontend submodule` |

### 브랜치 전략

- **메인 저장소**: `main` (안정 버전), `develop` (개발 버전)
- **서브모듈**: `main` (배포 가능 버전), `feature/*` (기능 개발)

---

## 🛠️ 트러블슈팅

### 문제 1: "modified content, untracked content"

**증상**: 서브모듈이 계속 수정된 것으로 표시됨

**해결**:
```bash
# 서브모듈 디렉토리로 이동
cd NeuroNova_03_front_end_react

# 변경 사항 확인
git status

# 불필요한 변경 사항 취소
git checkout .

# 또는 서브모듈 강제 리셋
git submodule update --init --force
```

### 문제 2: 서브모듈 디렉토리가 비어있음

**증상**: 클론 후 서브모듈 폴더가 빈 상태

**해결**:
```bash
# 서브모듈 초기화 및 업데이트
git submodule init
git submodule update
```

### 문제 3: 서브모듈의 원격 URL 변경

**해결**:
```bash
# .gitmodules 파일 수정
# url = <새로운_URL>

# 설정 동기화
git submodule sync

# 업데이트
git submodule update --init --recursive
```

---

## 📖 참고 자료

### 공식 문서
- [Git Submodules 공식 문서](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Git Submodules Tutorial](https://www.atlassian.com/git/tutorials/git-submodule)

### 관련 NeuroNova 문서
- [LOG_작업이력.md](LOG_작업이력.md) - Git 서브모듈 설정 이력
- [REF_CLAUDE_ONBOARDING_QUICK.md](REF_CLAUDE_ONBOARDING_QUICK.md) - 프로젝트 구조 설명
- [12_GCP_배포_가이드.md](12_GCP_배포_가이드.md) - 서브모듈 포함 배포 방법

---

## ✅ 체크리스트

### 서브모듈 작업 전

- [ ] 서브모듈이 최신 상태인지 확인 (`git submodule update --remote`)
- [ ] 서브모듈에서 올바른 브랜치 체크아웃 (`git checkout main`)
- [ ] 로컬 변경 사항이 없는지 확인 (`git status`)

### 서브모듈 작업 후

- [ ] 서브모듈에서 커밋 완료
- [ ] 서브모듈 원격 저장소에 푸시
- [ ] 메인 저장소에서 서브모듈 참조 업데이트 커밋
- [ ] 메인 저장소 원격 저장소에 푸시

---

**작성**: NeuroNova Development Team
**최종 업데이트**: 2025-12-31
**문서 버전**: 1.0
