# 🔬 NF1-Smart-Redirector-Model: Faz 3 Laboratuvar ve Kalibrasyon Protokolleri

Bu döküman, in silico ortamda AlphaFold 3 ile kilitlenme başarısı doğrulanan ve GROMACS altyapısı kurulan **SRX-RNA01 yapay RNA-Aptamer sisteminin** ıslak laboratuvar (wet-lab) ortamında sentezlenmesi, karakterizasyonu ve Genetik Algoritma destekli SDE/ODE tabanlı hesaplamalı model parametrelerinin deneysel verilere göre kalibre edilmesi için Standart Operasyon Prosedürlerini (SOP) içerir.

## 🛡 Protokol 1: Yapay RNA Modifikasyonu ve Stabilizasyon

SRX-RNA01 yapay RNA molekülünün hücre içi nükleazlar (RNase) tarafından parçalanmasını önlemek ve yapısal kararlılığını korumak amacıyla kimyasal modifikasyon stratejisi uygulanmıştır.

### Reaktif Reçetesi
- **Sentez Tasarımı:** 75-nt uzunluğundaki SRX-RNA01 dizisi, dizilim boyunca fosforotiyoat (PS) bağları, pirimidinlerde 2'-Flor (2'-F) ve pürinlerde 2'-O-Metil (2'-OMe) modifikasyonları içerecek şekilde katı-faz oligonükleotid senteziyle üretilir.
- **Molar Çözelti:** 1.0 mg/mL modifiye RNA stok konsantrasyonu (50 mM Sodyum Sitrat Tamponu, pH 4.0 içinde). Pozitif yük optimizasyonu için pH kritik eşiktedir.

### Deneysel Basamaklar
1. Sentetik olarak üretilen modifiye SRX-RNA01 liyofilize tozunu sodyum sitrat tamponunda çözün.
2. Doğru ikincil yapının (hairpin/loop konformasyonu) oluşması için çözeltiyi termal döngü cihazında 95°C'ye ısıtın.
3. 95°C'de 5 dakika beklettikten sonra, cihazı kapatarak çözeltinin oda sıcaklığına (25°C) yavaşça (annealing) soğumasını sağlayın.
4. Katlanmış RNA yapısını LNP enkapsülasyon adımına aktarmak üzere 4°C'de muhafaza edin.

## 💊 Protokol 2: Lipid Nanopartikül (LNP) Kapsülleme

Modifiye edilmiş yapay RNA yapısının negatif yük bariyerlerini aşarak sitoplazmaya kararlı geçiş yapabilmesi amacıyla mikrofluidik çip üzerinde kontrollü enkapsülasyon sürecidir.

### 1. Lipid (Organik) Faz Bileşimi (Mutlak Alkol İçinde)
- **DLin-MC3-DMA (İyonize Katyonik Lipid):** %50 Molar (RNA fosfat gruplarını hapsetmek için)
- **DSPC (Yardımcı Yapısal Lipid):** %10 Molar
- **Kolesterol (Stabilizasyon Ajanı):** %38.5 Molar
- **DMG-PEG2000 (Pegile Lipid):** %1.5 Molar (Yüzey kalkanı oluşturmak için)

### 2. Sulu Faz Bileşimi
- Katlanmış modifiye SRX-RNA01 molekülü, **50 mM Sodyum Sitrat Tamponu (pH 4.0)** içerisinde çözülmüş halde tutularak iyonize lipidlerle elektrostatik etkileşime girmesi sağlanır.

### 3. Micro-Akışkan Parametreleri
- **Akış Hızı Oranı (FRR):** Sulu Faz : Organik Faz = 3 : 1
- **Toplam Akış Hızı (TFR):** > 12 mL/dk (Homojen dağılım için kritik alt sınır)
- **Nihai İşlem:** Sentezlenen LNP süspansiyonu süratle sterile 1X PBS (pH 7.4) tamponuna karşı 4°C'de diyaliz edilerek etanol tamamen uzaklaştırılır ve dış faz nötrleştirilir.

## 🧬 Protokol 3: Hesaplamalı Model Kalibrasyonu (Structure-Informed SDE Sync)

`simulations/confinement_analyzer.py` içerisindeki Stokastik Diferansiyel Denklem (SDE) ve global kararlılık motorunun parametrelerinin deneysel in vitro verilerle kalibre edilmesi sürecidir.

### Deneysel Basamaklar
1. **Hücre Modeli:** NF1 mutant Schwannoma veya MPNST (Malign Peripheral Nerve Sheath Tumor) hücre hatları kültüre edilir.
2. **Doz-Yanıt Protokolü:** Hücrelere farklı konsantrasyonlarda (0-100 nM) tasarlanan SRX-RNA01-LNP formülasyonu uygulanır.
3. **Kinetik Ölçüm:** İlaç uygulamasından sonraki 0, 15, 30, 60, 120 ve 240. dakikalarda hücre lizatları toplanır. Western Blot ve ELISA yöntemleriyle aktif **KRAS-GTP** ve fosforile **pERK1/2** sinyal genlikleri nicel olarak ölçülür.
4. **Matematiksel Curve Fitting & Parametrik Eşleme:** Elde edilen zaman-konsantrasyon grafikleri ve 72 saatlik MTT/XTT proliferasyon verileri, Python'daki `bridge_models/evidence_weighted_calibration.py` kalibratörüne gömülü olan non-linear Hill saturasyon fonksiyonuna fit edilir:
    - **C_eff Katsayısının Kilitlenmesi:** HADDOCK 2.4'ten elde edilen $-71.8 \pm 5.1$ skoru, Hill kooperativite sabiti ($n=2.0$) ve yarı-saturasyon sabiti ($K_{half}=75.0$) parametreleri altında işlenerek $C_{eff} = 0.4519$ olarak kilitlenir.
    - **τ (Gecikme) Modülasyonu:** Zaman serisi Western Blot analizlerindeki pERK1/2 sinyal faz kaymaları, bazal gecikmenin $\tau_{eff} = \tau_0 \cdot (1 + \alpha \cdot C_{eff})$ formülüyle $\tau_{eff} = 2.36$ değerine kalibre edilmesiyle eşlenir. Bu durum, ligandın konformasyonel nefes alma (conformational breathing) dinamiklerini doğrular.
    - **σ (Volatilite) Azaltımı:** Hücre içi stokastik fluktuasyonların baskılanma derecesi, gürültü katsayısının $\sigma_{eff} = \sigma_0 \cdot (1 - \beta \cdot C_{eff})$ formülü üzerinden $\sigma_{eff} = 0.43$ değerine sönümlenmesiyle kalibre edilir.

## 📊 Protokol 4: Kalite Kontrol (QC) & Topolojik Sınır Değerleri

Sentez ve kalibrasyon sonrası ekibin onaylaması gereken kalite ve kararlılık kriterleri:
- **DLS Analizi:** Dinamik Işık Saçılması ile hidrodinamik çap = 80 - 120 nm aralığında olmalı, PDI (Polidispersite İndeksi) < 0.18 seviyesinde kalmalıdır.
- **Enkapsülasyon Verimi (%EE):** RiboGreen floresan testi ile ölçülen RNA hapsetme başarısı %EE > %80 olmalıdır.
- **Nükleaz Kararlılığı:** %10 Fetal Bovine Serum (FBS) içeren ortamda 24 saat inkübasyon sonrası Agaroz Jel Elektroforezinde RNA bandının bütünlüğü korunmalıdır.
- **Stokastik Havza & Frekans Filtreleme Doğrulaması:** Kalibre edilen parametreler Ornstein–Uhlenbeck renkli gürültü testine tabi tutulduğunda, Welch metoduyla hesaplanan Güç Spektrumu Yoğunluğu (PSD) analizi, patolojik mutant kaskat üzerinde **net %23.35 oranında bir gürültü bastırma performansı** sergilemelidir. Bu spektral filtreleme gücü, sistemin Lyapunov potansiyel kuyusundan kaçış olasılığını (Stochastic Basin Escape) $<%1.0$ sınırında tutarak metastable confinement rejimini wet-lab kinetiğinde de doğrulamalıdır.

## 🧬 Protokol 5: Genetik Algoritma Şampiyon Sekans Entegrasyonu (Yeni)

`optimization/genetic_optimizer.py` tarafından evrimsel döngüler (Crossover & Mutation) sonucunda en yüksek fitness skoruna ulaşarak seçilen "Şampiyon Dizilimler" için uygulanacak adımlar:
1. **Dizi İzleme ve Sentez:** Algoritmanın `🥇 En İyi Aday Sekans:` terminal çıktısı olarak verdiği 30-nt uzunluğundaki RNA dizilimleri doğrudan hedef primer oligonükleotid dizilimi olarak kabul edilir.
2. **Kombinatoryal Validasyon:** Algoritmanın ürettiği ilk 3 şampiyon varyasyon, eş zamanlı olarak sentezlenerek Protokol 3'teki in vitro doz-yanıt testine alınır.
3. **Fitness Skor Doğrulaması:** Islak laboratuvarda ölçülen `residual_leakage` (rezidüel sızıntı) tabanı değerinin, in silico optimizasyonun hedef fonksiyonundaki **%5.5 (0.055)** eşiğine olan mutlak uzaklığı ölçülerek algoritmanın tahmin doğruluğu (r2 skoru) tescillenir.

