# 🚀 Enterprise AI Knowledge Assistant: Complete Run & Deployment Guide
*(लोकल Run करण्यापासून ते Production Deployment पर्यंतची संपूर्ण Step-by-Step नियमावली)*

---

## 📋 Overview of What We Will Cover

या गाईडमध्ये खालील सर्व पद्धती स्टेप-बाय-स्टेप दिल्या आहेत:
1. **Prerequisites & API Key Setup** (सुरुवातीची तयारी)
2. **Method 1: Local Development Run** (Python Virtual Environment द्वारे चालवणे)
3. **Method 2: Running All 34 Automated Tests** (चाचणी करणे)
4. **Method 3: Docker & Docker Compose Run** (कंटेनर्समध्ये चालवणे)
5. **Method 4: Monitoring Stack Run** (Prometheus, Loki, Grafana चालवणे)
6. **Method 5: Kubernetes Production Deployment** (K8s क्लस्टरवर डिप्लॉय करणे)
7. **Method 6: GitHub Actions CI/CD Pipeline** (क्लाउडवर ऑटोमॅटिक बिल्ड & टेस्ट)
8. **Interview/Client Live Demo Walkthrough** (डेमो कसा दाखवायचा)

---

## 🔑 Step 0: Prerequisites & API Key Setup

### १. Google Gemini API Key मिळवणे:
RAG synthesis साठी Google Gemini API आवश्यक आहे.
1. [Google AI Studio](https://aistudio.google.com/) वर जा.
2. मोफत **Gemini API Key** जनरेट करा.
3. तुमच्या प्रोजेक्टच्या `.env` फाईलमध्ये ती की सेट करा:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
*(टीप: जर तुमच्याकडे Gemini API Key तात्पुरती नसेल, तरीही सर्च, टेक्स्ट एक्स्ट्रॅक्शन आणि व्हेक्टर डेटाबेस 100% चालतो.)*

---

## 💻 Method 1: Local Development Run (Python Virtual Environment)

हा पर्याय सर्वात सोपा आणि जलद आहे. कोड एडिट करून लगेच आउटपुट पाहण्यासाठी हा वापरतात.

### पायरी १: व्हर्च्युअल एन्व्हायरनमेंट ॲक्टिव्हेट करा
PowerShell ओपन करून खालील कमांड रन करा:
```powershell
cd C:\AI-Knowledge-Assistant
.venv\Scripts\Activate.ps1
```

### पायरी २: FastAPI Backend सुरू करा (Terminal 1)
```powershell
.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend URL:** `http://localhost:8000`
- **Interactive Swagger API Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`
- **Prometheus Metrics:** `http://localhost:8000/metrics`

### पायरी ३: Streamlit Frontend सुरू करा (Terminal 2)
एक नवीन PowerShell विंडो उघडा आणि रन करा:
```powershell
cd C:\AI-Knowledge-Assistant
.venv\Scripts\streamlit run frontend/app.py --server.port 8501
```
- **Web UI URL:** `http://localhost:8501`

👉 **ब्राउझरमध्ये उघडा:** तुमच्या क्रोम किंवा एज ब्राउझरमध्ये `http://localhost:8501` ओपन करा. तिथे तुम्हाला PDF अपलोड आणि RAG Chat Assistant दिसेल!

---

## 🧪 Method 2: Running Automated Unit & Integration Tests

सिस्टममधील सर्व 34 टेस्ट्स (API, PDF, RAG, Docker, K8s, Monitoring, CI/CD) पास होतात का हे तपासण्यासाठी:

```powershell
cd C:\AI-Knowledge-Assistant
.venv\Scripts\python -m unittest discover tests
```

**अपेक्षित आउटपुट (Expected Output):**
```text
Ran 34 tests in 4.102s
OK
[SUCCESS] FastAPI /health logic passed!
[SUCCESS] Ingested 2 chunks into ChromaDB!
[SUCCESS] Query 1 correctly retrieved Page 1!
```

---

## 🐳 Method 3: Containerized Run with Docker & Docker Compose

जर तुम्हाला संपूर्ण ॲप्लिकेशन Docker कंटेनर्समध्ये Production Mode मध्ये चालवायचे असेल:

### पायरी १: Docker Desktop चालू असल्याची खात्री करा
तुमच्या Windows टास्कबारमध्ये Docker Desktop चालू (Running) असावे.

### पायरी २: कंटेनर्स बिल्ड आणि स्टार्ट करा
```bash
cd C:\AI-Knowledge-Assistant

# बिल्ड आणि बॅकग्राऊंडमध्ये स्टार्ट करा
docker compose up -d --build
```

### पायरी ३: कंटेनर्सची स्थिती तपासा
```bash
docker compose ps
```
दोन्ही कंटेनर्स (`backend` आणि `frontend`) **healthy** आणि **Up** दिसतील.

### पायरी ४: लाईव्ह लॉग्ज पाहण्यासाठी
```bash
# बॅकएंडचे लॉग्ज पाहणे
docker compose logs -f backend

# फ्रंटएंडचे लॉग्ज पाहणे
docker compose logs -f frontend
```

### पायरी ५: कंटेनर्स थांबवण्यासाठी
```bash
docker compose down
```
*(टीप: `pdf_data` आणि `chroma_data` हे Named Volumes असल्याने डेटा डिलीट होत नाही.)*

---

## 📊 Method 4: Monitoring & Observability Stack (Prometheus + Grafana + Loki)

प्रोजेक्टचे लाईव्ह मेट्रिक्स, लेटन्सी आणि कंटेनर लॉग्ज ट्रॅक करण्यासाठी:

### पायरी १: मॉनिटरिंग स्टॅक सुरू करा
```bash
cd C:\AI-Knowledge-Assistant
docker compose -f monitoring/docker-compose.monitoring.yml up -d
```

### पायरी २: डॅशबोर्ड्स ब्राउझरमध्ये उघडा
1. **Grafana:** `http://localhost:3000`
   - *Username:* `admin`
   - *Password:* `admin`
   - डॅशबोर्ड्समध्ये जाऊन **"Enterprise AI Knowledge Assistant"** डॅशबोर्ड निवडा. तिथे API Latency, Request Rate, आणि ChromaDB Vector Count चे ग्राफ्स दिसतील.
2. **Prometheus:** `http://localhost:9090`
   - Status -> Targets मध्ये जाऊन तपासा की FastAPI बॅकएंड 5 सेकंदांच्या अंतराने स्क्रॅप होत आहे.
3. **Loki:** `http://localhost:3100` (लॉग अ‍ॅग्रिगेशन इंजिन).

### थांबवण्यासाठी:
```bash
docker compose -f monitoring/docker-compose.monitoring.yml down
```

---

## ☸️ Method 5: Kubernetes (K8s) Production Deployment

हा एंटरप्राइझ लेव्हल डिप्लॉयमेंटचा टप्पा आहे (उदा. AWS EKS, Google GKE, Azure AKS, किंवा लोकल Minikube/Kind).

### पायरी १: K8s क्लस्टर कनेक्ट करा (उदा. Minikube)
```bash
# जर लोकल Minikube वापरत असाल
minikube start
```

### पायरी २: १-क्लिक Kustomize द्वारे सर्व मॅनिफेस्ट्स लागू करा
```bash
cd C:\AI-Knowledge-Assistant
kubectl apply -k k8s/
```
या एका कमांडने खालील सर्व गोष्टी क्लस्टरवर तयार होतात:
- `ConfigMap` आणि `Secrets`
- `pdf-storage-pvc` (1Gi) आणि `chroma-storage-pvc` (2Gi)
- `backend-deployment` (2 Replicas) + `backend-service` (ClusterIP: 8000)
- `frontend-deployment` (2 Replicas) + `frontend-service` (NodePort: 30501)

### पायरी ३: डिप्लॉयमेंट आणि पॉड्सची स्थिती तपासा
```bash
kubectl get pods -o wide
kubectl get svc
kubectl get pvc
kubectl rollout status deployment/backend-deployment
kubectl rollout status deployment/frontend-deployment
```

### पायरी ४: ॲप्लिकेशन ॲक्सेस करा
- जर Cloud Kubernetes असेल: LoadBalancer External IP द्वारे ॲक्सेस करा.
- जर Minikube असेल:
  ```bash
  minikube service frontend-service
  ```
  किंवा थेट NodePort द्वारे: `http://<Node-IP>:30501`

### K8s मधील सर्व रिसोर्सेस डिलीट करण्यासाठी:
```bash
kubectl delete -k k8s/
```

---

## 🔄 Method 6: CI/CD Pipeline (GitHub Actions Automation)

आपण `.github/workflows/ci-cd.yml` आधीच कॉन्फिगर करून GitHub वर पुश केले आहे.

### ही पाईपलाईन कशी ट्रिगर होते?
जेव्हा तुम्ही कोडमध्ये बदल करून GitHub वर पुश करता:
```powershell
git add .
git commit -m "feat: new improvement"
git push origin main
```

### काय घडते? (3 स्वयंचलित स्टेजेस):
1. **GitHub Actions Runner सुरू होतो.**
2. **Stage 1 (Unit & Integration Tests):** 
   - सर्व 34 युनिट टेस्ट्स चालवून कोड सुरक्षित असल्याची खात्री होते.
3. **Stage 2 (Docker Build & Scan):** 
   - Backend आणि Frontend चे डॉकर इमेजेस आपोआप बिल्ड होतात.
4. **Stage 3 (Kubernetes Dry-Run Validation):** 
   - सर्व K8s मॅनिफेस्ट्सची सिंटॅक्स आणि स्कीमा तपासली जाते (`kubectl apply --dry-run=client -k k8s/`).

👉 **लाईव्ह पाहण्यासाठी:** तुमच्या GitHub रिपॉझिटरीवरील **"Actions"** टॅबवर जा:  
`https://github.com/Pavan7856/AI-Knowledge-Assistant/actions`

---

## 🎬 8. Live Demo Walkthrough (इंटरव्ह्यू किंवा सादरीकरणासाठी)

जर तुम्हाला कोणाला हा प्रोजेक्ट लाईव्ह चालवून दाखवायचा असेल, तर या ४ सोप्या पायऱ्या फॉलो करा:

1. **ॲप्लिकेशन सुरू करा:** 
   - `uvicorn backend.main:app` (Backend)
   - `streamlit run frontend/app.py` (Frontend)
2. **Tab 1 उघडा (Document Ingestion):**
   - कोणताही तांत्रिक PDF अपलोड करा (उदा. Kubernetes Docs, Python Manual).
   - "Upload & Ingest PDF" बटनावर क्लिक करा.
   - दाखवा: "कशाप्रकारे अवघ्या १ सेकंदात PyMuPDF ने मजकूर काढला, Recursive Text Splitter ने 700 अक्षरांचे चंक्स केले, आणि ChromaDB मध्ये वेक्टर्स साठवले गेले!"
3. **Tab 2 उघडा (RAG Assistant):**
   - डॉक्युमेंटवर आधारित अवघड प्रश्न विचारा.
   - दाखवा: "AI ने उत्तर देताना खाली हिरव्या रंगात `[Source: Page X]` असा पुरावा दिला आहे, ज्यामुळे Hallucination चा धोका शून्य होतो!"
4. **Tab 3 उघडा (System Health & Architecture):**
   - ChromaDB मधील लाइव्ह Chunk Count आणि आर्किटेक्चर डायग्राम दाखवा.
   - `/metrics` एंडपॉइंट उघडून Prometheus मेट्रिक्स दाखवा.

---

## 📌 Summary Commands Table

| कार्य (Task) | चालवण्याची नेमकी कमांड (Exact Command) |
| :--- | :--- |
| **सर्व टेस्ट्स चालवणे** | `.venv\Scripts\python -m unittest discover tests` |
| **लोकल बॅकएंड चालवणे** | `.venv\Scripts\uvicorn backend.main:app --port 8000 --reload` |
| **लोकल फ्रंटएंड चालवणे** | `.venv\Scripts\streamlit run frontend/app.py --server.port 8501` |
| **डॉकर कंटेनर्स चालवणे** | `docker compose up -d --build` |
| **डॉकर कंटेनर्स थांबवणे** | `docker compose down` |
| **मॉनिटरिंग स्टॅक चालवणे**| `docker compose -f monitoring/docker-compose.monitoring.yml up -d` |
| **कुबरनेटीसवर डिप्लॉय करणे**| `kubectl apply -k k8s/` |
| **GitHub वर कोड पुश करणे**| `git push origin main` |
