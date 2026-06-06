# 📑 Dynamic Integration Protocol: Core GRT & Attractor Manifold Bridge

This document details the architectural link and state-dependent feedback loop between the Core Biochemical Engine and the Attractor Manifold Sandbox.

## 🏛️ Architectural Topology: The Hybrid Bridge

Rather than forming a hard-coded geometric constraint directly into the precise system, the protocol employs a dynamic, state-dependent coupling layer.

```text
[ coupled_ode_v1.py ] (Core Biochemical Engine)
│
▼
Composite Stress Index (S_t) ───► Threshold S_c (Exceeded?)
│                                 │
▼ (No: Homeostasis)               ▼ (Yes: Pathological)
▼                                 ▼
[ Natural Relaxation ]            [ Trigger Manifold Switch (f_s) ]
                                  │
                                  ▼
                                  [ Fetch Confinement Factor ]
                                  From: attractor_manifold_sandbox.py
                                  │
                                  ▼
                                  k_prod Dynamic Attenuation
                                  │
                                  ▼
                                  [ Target Attractor Confinement ]
```

## 📐 Mathematical Coupling Formulation

When the integration bridge flag `use_attractor_manifold` is enabled, the system evaluates the coupling activation function:

$$\text{If } S_t > S_c \implies f_s = \frac{E_{rt}^2}{S_t + E_{rt}^2}$$

$$\text{Confinement Factor } (\mathcal{C}) = \frac{\sqrt{R_{\text{max}}^2 - S_t^2}}{R_{\text{max}}}$$

The modulated production flow ($k_{\text{prod}}^{(t)}$) feeding the $dX[A]/dt$ differential equation is attenuated using the computed confinement metrics:

$$k_{\text{prod}}^{(t)} = k_{\text{prod}} \cdot \left[1.0 - f_s \cdot (1.0 - \mathcal{C})\right]$$


### 💎 Strategic Advantages of this Coupling:
* **Zero Singularity Risk ($f_s \rightarrow \text{Stabilization}$):** The integration employs safe asymptotic bounds to prevent division-by-zero errors.
* **Minimal Functional Disturbance:** For baseline homeostatic breathing ($S_t \le S_c$), the feedback loop remains completely dormant.
* **Phenomenological Distortion:** In hyper-activated states, the production rate smoothly scales down to guarantee stability.

## ⚙️ Implementation Parameters


To switch between the standalone biochemical model and the integrated attractor framework, adjust the configuration dictionary in your execution script:

```python
base_param = {
    # ... Core Biological Coefficients ...
    
    # --- MANIFOLD INTEGRATION CONFIGURATION ---
    'use_attractor_manifold': True,   # Enables/Disables the sandbox interface
    'S_threshold': 1.2,               # Advanced Engine Selectivity Baseline
    'R_max_confinement': 2.5          # Target Attractor Scale radius
}
```

---

## ⏳ Extended Coupling: State-Dependent Dynamic Delay & Oscillatory Feedback

To evaluate the system under realistic intracellular latencies without modifying legacy deterministic flags, a state-dependent phase-lag extension has been formulated.

### 🏛 Architectural Integration

The independent module `simulations/delay_coupled_bifurcation.py` bypasses the static thresholds (\(S_c\)) and tracks global structural stability under dynamic, signal-mediated history-buffer allocations (\(\tau_{eff}(x)\)).

```text
[ Unstable Runaway Flow ] (t < t_activation)
         │
         ▼ (t >= t_activation Onset)
[ Compute Dynamic Latency ] ───► Overload Damping: tau_eff = f(x_current)
         │
         ▼
[ Non-Linear Hill Confinement ] ───► Memory State Retrieval: x(t - tau_eff)
         │
         ▼
[ Bounded Metastable Oscillator ] (State-Dependent Hopf Transition)
```

### 📐 Mathematical Formulation

When analyzing the temporally distributed regulatory feedback, the finite difference integrator tracks state trajectories via an explicit state-dependent history loop:

$$\text{If } t \ge t_{\text{activation}} \implies \frac{dy}{dt} = -r \cdot x(t - \tau_{\text{eff}}) + \left( R^2 - x^2 - y^2 \right) \cdot y \cdot \text{Hill}(x)$$

Where the cumulative cascade propagation latency $\tau_{\text{eff}}$ scales dynamically based on downstream receptor saturation kinetics:

$$\tau_{\text{eff}}(x) = \tau_{\text{baseline}} + \tau_{\text{max}} \cdot \frac{x^2}{K_{\tau}^2 + x^2}$$

Under this formulation, the system undergoes a stable **Delay-Induced Hopf Bifurcation**, transforming the fixed-point geometric boundary into an asymmetric, macroscopically bounded **Stable Limit Cycle Attractor** exhibiting metabolic breathing characteristics.

### 🌌 Phenomenological Visual Analogy: Phase-Space Spotting & Manifold Black-Out

Under extreme pathway deregulation, the state-dependent phase lag acts as a temporal trap. When a damaged cell's trajectory becomes structurally confined within its own delayed feedback loops, it forms dense trajectory clusterings—phenomenologically resembling localized "spots" (local phase-space attractors) in the phase portrait. As metabolic saturation increases ($\tau_{\text{eff}} \rightarrow \tau_{\text{max}}$), these localized spots expand, destabilize, and overlap into dense, chaotic complex manifolds, effectively visualizing a structural "manifold black-out" where the cell is permanently trapped inside its own irreversible oncogenic feedback geometry.

---

# 📑 Dinamik Entegrasyon Protokolü: Çekirdek GRT ve Atraktör Manifoldu Köprüsü

Bu doküman, Çekirdek Biyokimyasal Motor (Core Biochemical Engine) ile Atraktör Manifoldu Simülasyon Alanı (Attractor Manifold Sandbox) arasındaki mimari bağıntıyı ve duruma bağlı geri besleme döngüsünü detaylandırmaktadır.

## 🏛️ Mimari Topoloji: Hibrit Köprü

Protokol, hassas sistem içinde katı kodlanmış (hard-coded) geometrik bir kısıtlama oluşturmak yerine; dinamik ve duruma bağlı bir kuplaj (bağlaşım) katmanı kullanır.

```text
[ coupled_ode_v1.py ] (Çekirdek Biyokimyasal Motor)
│
▼
Kompozit Stres İndeksi (S_t) ───► Eşik Değeri S_c (Aşıldı mı?)
│                                 │
▼ (Hayır: Homeostaz)              ▼ (Evet: Patolojik)
▼                                 ▼
[ Doğal Gevşeme ]                 [ Manifold Geçişini Tetikle (f_s) ]
                                  │
                                  ▼
                                  [ Sınırlama Faktörünü Getir ]
                                  Kaynak: attractor_manifold_sandbox.py
                                  │
                                  ▼
                                  k_prod Dinamik Zayıflatma
                                  │
                                  ▼
                                  [ Hedef Atraktör Sınırlaması ]
```

## 📐 Matematiksel Kuplaj Formülasyonu

Entegrasyon köprüsü bayrağı `use_attractor_manifold` etkinleştirildiğinde, sistem kuplaj aktivasyon fonksiyonunu hesaplar:

$$\text{Eğer } S_t > S_c \implies f_s = \frac{E_{rt}^2}{S_t + E_{rt}^2}$$

$$\text{Sınırlama Faktörü } (\mathcal{C}) = \frac{\sqrt{R_{\text{max}}^2 - S_t^2}}{R_{\text{max}}}$$

The $dX[A]/dt$ diferansiyel denklemini besleyen modüle edilmiş üretim akışı ($k_{\text{prod}}^{(t)}$), hesaplanan sınırlama metrikleri kullanılarak zayıflatılır:

$$k_{\text{prod}}^{(t)} = k_{\text{prod}} \cdot \left[1.0 - f_s \cdot (1.0 - \mathcal{C})\right]$$

### 💎 Bu Kuplajın Stratejik Avantajları:
* **Sıfır Tekillik Riski ($f_s \rightarrow \text{Stabilizasyon}$):** Entegrasyon, sıfıra bölünme hatalarını önlemek için güvenli asemptotik sınırlar kullanır.
* **Minimum Fonksiyonel Bozulma:** Standart homeostatik solunum için ($S_t \le S_c$), geri besleme döngüsü tamamen pasif (uyku modunda) kalır.
* **Fenomenolojik Bozulma Önleme:** Aşırı aktifleşmiş durumlarda, stabiliteyi garanti altına almak için üretim hızı pürüzsüz bir şekilde aşağı doğru ölçeklendirilir.

## ⚙️ Uygulama Parametreleri

Bağımsız çalışan biyokimyasal model ile entegre atraktör çerçevesi arasında geçiş yapmak için, yürütme betiğinizdeki konfigürasyon sözlüğünü ayarlayın:

```python
base_param = {
    # ... Çekirdek Biyolojik Katsayılar ...
    
    # --- MANİFOLD ENTEGRASYON KONFİGÜRASYONU ---
    'use_attractor_manifold': True,   # Simülasyon alanı arayüzünü etkinleştirir/devre dışı bırakır
    'S_threshold': 1.2,               # Gelişmiş Motor Seçicilik Eşiği
    'R_max_confinement': 2.5          # Hedef Atraktör Ölçek yarıçapı
}
```

---

## ⏳ Genişletilmiş Bağlaşım: Duruma Bağlı Dinamik Gecikme ve Osilatör Geri Beslemesi

Çekirdek modelin kararlı deterministik yapısını bozmadan; hücre içi zaman gecikmelerinin sistem üzerindeki etkisini incelemek amacıyla yapıya duruma bağlı dinamik bir faz farkı (state-dependent phase lag) katmanı eklenmiştir.

### 🏛 Mimari Entegrasyon

Bağımsız `simulations/delay_coupled_bifurcation.py` modülü, anlık sinyal genliğine bağlı olarak değişen bir gecikme fonksiyonu $\tau_{\text{eff}}(x)$ kullanarak, geçmiş durum hafızası üzerinden küresel kararlılık eğrilerini test eder.

### 📐 Matematiksel Formülasyon

Zamansal olarak dağıtılmış dinamik düzenleyici geri besleme analiz edilirken, integratör yörüngeleri hücre içi protein doygunluk kinetiğine bağlı bir kuplaj döngüsü üzerinden izler:

$$\text{Eğer } t \ge t_{\text{activation}} \implies \frac{dy}{dt} = -r \cdot x(t - \tau_{\text{eff}}) + \left( R^2 - x^2 - y^2 \right) \cdot y \cdot \text{Hill}(x)$$

Burada kümülatif hücresel iletim gecikmesi $\tau_{\text{eff}}$, sinyal yoğunluğu arttıkça nükleer transport ve taşıyıcı mekanizmaların doyuma ulaşmasıyla dinamik olarak uzar:

$$\tau_{\text{eff}}(x) = \tau_{\text{baseline}} + \tau_{\text{max}} \cdot \frac{x^2}{K_{\tau}^2 + x^2}$$


