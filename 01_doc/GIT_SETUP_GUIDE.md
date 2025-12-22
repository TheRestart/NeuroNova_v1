# GitHub 다중 저장소(Multi-Repo) 설정 가이드

이 프로젝트는 3개의 독립적인 GitHub 저장소로 관리되도록 구성되었습니다.

## 저장소 구조

1. **Back End** (`02_back_end/`)
   - 포함: Django Server, OpenEMR Server Docker 설정
   - `git init` 완료됨
2. **Front End - React** (`03_front_end_react/`)
   - 포함: React Web Application (`01_react_client`)
   - `git init` 완료됨
3. **Front End - Flutter** (`04_front_end_flutter/`)
   - 포함: Mobile Application
   - `git init` 완료됨

(참고: 최상위 루트 폴더는 문서 관리를 위한 별도 저장소로 사용하거나 로컬 워크스페이스로만 사용할 수 있습니다.)

## GitHub 연동 방법

각 폴더에서 다음 명령어를 실행하여 GitHub에 Push 하세요.

### 1. Back End (Django)
```bash
cd 02_back_end
# GitHub에서 'cdss-backend' 같은 이름으로 새 리포지토리 생성 후:
git remote add origin <BACKEND_REPO_URL>
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 2. Front End (React)
```bash
cd 03_front_end_react
# GitHub에서 'cdss-frontend-react' 같은 이름으로 새 리포지토리 생성 후:
git remote add origin <REACT_REPO_URL>
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 3. Front End (Flutter)
```bash
cd 04_front_end_flutter
# GitHub에서 'cdss-frontend-flutter' 같은 이름으로 새 리포지토리 생성 후:
git remote add origin <FLUTTER_REPO_URL>
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 3. 문서 및 관리 (Root)
만약 최상위 `doc` 및 `UML` 파일도 버전 관리를 하려면:
```bash
cd .  # 루트 디렉토리
# GitHub에서 'cdss-docs' 같은 이름으로 새 리포지토리 생성 후:
git remote add origin <DOCS_REPO_URL>
git add .
git commit -m "Initial commit"
git push -u origin main
```
*주의: 루트 저장소의 `.gitignore`에는 하위 저장소 폴더가 이미 등록되어 있어 중복 커밋을 방지합니다.*
