# 🌌 Adaptive Multi-Threshold Proteostatic Regulation Framework (AMTPRF)
*Nonlinear Adaptive Signaling Framework for Exploratory Systems-Level Simulations.*

⚠️ **CRITICAL DISCLAIMER:** This module represents a conceptual, non-validated, and exploratory synthetic biology architecture operating under phenomenological regime labels. Astrophysics and mathematical metaphors used herein function strictly as qualitative behavior models (state-transition regimes) rather than literal biochemical mechanisms.

## 1. Giriş ve Kararlı Çekim Alanı Geçişi (Attractor Basin Transition)
The framework explores whether adaptive threshold-governed signaling control architectures can theoretically stabilize pathological signaling loads without requiring continuous inhibitory pressure. 

Model, patolojik proliferatif kararlılık alanındaki (**Attractor State A**) sinyal yükünü kronik olarak baskılamak yerine; doğrusal olmayan geri bildirim ağları vasıtasıyla sistemi kontrol altına alarak, metastabil bir dinamik ağ üzerinden geri dönüşümsüz, düşük enerjili ve bölünmeyen bir uyuşukluk/yaşlanma çekim havzasına (**Attractor State B - Absorbing Senescent Basin**) taşımayı hedefler.

## 2. Sürekli Rejim Entegrasyonu ve Matematiksel Mimari (Continuous Regime Interpolation)

### 📊 A. Çift Kademeli Doğrusal Olmayan Temizlik Modeli (Two-Tiered Regime Blending)
Sistemde numerik integrasyonu kararsızlaştıran keskin eşik geçişleri (hard thresholds) yerine, diferansiyel sürekliliği koruyan ve Jacobian analizine izin veren sigmoid tabanlı rejim harmanlaması (Regime Blending) kurgulanmıştır:

\[\sigma_1(M) = \frac{1}{1 + e^{-k_1(M - M_{c1})}} \quad \text{(Catastrophic Clearance Weight)}\]
\[\sigma_2(M) = \frac{1}{1 + e^{-k_2(M - M_{c2})}} \quad \text{(Absorbing Senescent Sink Weight)}\]

*   **Rejim I: Catastrophic Clearance Regime (Hızlı Doğrusal Olmayan Temizlik):** Sinyal yükü hafıza çekirdeğinde ilk geçiş merkezini ($M_{c1}$) uyardığında devreye giren hızlı ve hedefli moleküler temizlik fazıdır (**Rapid Nonlinear Clearance**).
*   **Rejim II: Absorbing Senescent Basin & Topological State Isolation:** Sinyal yükünün ekstrem fazlara ulaşması durumunda, kopyalama katsayısı fenomenolojik olarak saptırılır (**phenomenological diversion coefficient** $\rightarrow 0$), proliferatif ağ ile olan bağ kesilir ve hücre geri dönüşümsüz düşük enerjili durağan bir faza (**Irreversible Low-Energy Sink State**) yönlendirilir.

---

## 3. Stokastik Dinamikler ve Fokker-Planck Enerji Peyzajı (Energy Landscape Theory)

### 🎲 A. Langevin Stokastik Gürültü Modeli
Hücre içi transkripsiyon patlamaları (transcription bursts) ve moleküler gürültülerin (shot noise) sistem kararlılığı üzerindeki etkisini ölçmek amacıyla, deterministik drift (sürüklenme) terimleri Wiener Süreci ($dW_t$) ve Brownian dalgalanmalarıyla birleştirilerek Langevin Stokastik Diferansiyel Denklemlerine (SDE) dönüştürülmüştür:
\[dX_i = f_i(X, t)dt + \sigma_i dW_t\]
*Burada $\sigma_i$ katsayısı, sistemin yanlış pozitif aktivasyonlara karşı direncini (false activation resistance) belirleyen gürültü şiddetini temsil eder.*

### 🏔️ B. Olasılık Yoğunluğu ve Global Enerji Minimumu (Sink State Transition)
Langevin yörüngelerinin zamanla nasıl bir olasılık dağılımına dönüştüğü ve kararlılık vadileri arasındaki geçiş olasılıkları (transition probability) Fokker-Planck kısmi diferansiyel denklemi ile modellenmiştir:
\[\frac{\partial P(x,t)}{\partial t} = -\sum_{i} \frac{\partial}{\partial x_i} \left[ f_i(x)P(x,t) \right] + \sum_{i} \frac{\sigma_i^2}{2} \frac{\partial^2 P(x,t)}{\partial x_i^2}\]

Bu doğrultuda kurgulanan potansiyel enerji peyzajında ($V(x) = -\ln P_{ss}(x)$):
*   **Attractor State A (Patolojik Proliferatif Vadi):** Hücrenin gürültü dalgalanmalarıyla sürekli uyarıldığı, yüksek serbest enerjili, metastabil bir yarı-kararlı havzadır.
*   **Attractor State B (Absorbing Senescent Basin):** AMTPRF modülasyonu ve bellek çekirdeği ($M > 0.8$) tetiklendiğinde sistemin sığındığı, küresel olarak en kararlı, en düşük enerjili ve geri dönüşsüz yeni vadi (**Global Energy Minimum Sink**) olarak konumlandırılmıştır. Sistem gürültü şiddetine rağmen bu derin vadiden bir daha geri çıkamaz; böylece patolojik döngü tamamen kırılır.

---

## 4. Gelecek Araştırma Kapsamı ve Kısıtlamalar (Future Research Scope & Limitations)
Bu çalışma, konsept aşamasında bir hesaplamalı sistem biyolojisi çerçevesi (TRL-2) olduğundan, ilerleyen fazlarda derinleştirilmesi öngörülen hesaplamalı ve deneysel yol haritası şu şekildedir:

*   **A. Deneysel Parametre Kalibrasyonu (Data Fitting):** Modelde kullanılan idealize kinetik katsayılar, ilerleyen fazlarda NF1-mutant Schwann veya nörofibrom hücre hatlarından (in vitro Western Blot/Kütle Spektrometrisi) elde edilecek gerçek biyokimyasal veri setleri ile Monte Carlo Parametre Tahmini (Parameter Estimation) algoritmaları üzerinden kalibre edilecektir.
*   **B. Analitik Hopf Bifurkasyon Sınırları:** Sistem parametre uzayının limit döngüsü (osilasyon rejimi) sınırları, Jacobian matrisinin özdeğer spektrumunun gerçel kısmının sıfıra eşitlendiği durumlar ($\text{Re}(\lambda) = 0$) üzerinden analitik kararlılık eğrileri olarak matematiksel olarak türetilecektir.
*   **C. Fokker-Planck Sayısal Çözümü (Olasılık Peyzajı):** Langevin SDE motorundan elde edilecek binlerce stokastik yörüngenin histogram veri analizi yapılarak, durum uzayındaki çift kararlı potansiyel enerji peyzajının olasılık yoğunluk dağılım grafikleri (Probability Density Function Heatmap) görselleştirilecektir.


