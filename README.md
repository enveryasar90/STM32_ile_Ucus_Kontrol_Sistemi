# ✈️ STM32 Tabanlı Özel Uçuş Kontrolcüsü (Custom Flight Controller)

STM32 Nucleo-F446RE geliştirme kartı ve analog potansiyometreler kullanılarak geliştirilmiş, uçuş simülasyonları (War Thunder vb.) için sıfır gecikmeli, 3 eksenli (Roll, Pitch, Throttle) donanım ve yazılım projesidir.

Proje; mikrodenetleyici seviyesinde çok kanallı ADC okuma, DMA mimarisi, gürültü filtreleme algoritmaları, UART seri haberleşme ve Windows işletim sisteminde çalışan bir Python HID/vJoy köprüsünü uçtan uca bir araya getirir.

---

## 🎬 Proje Demosu

![Uçuş Kontrolcüsü Demo](media/surus.gif)

---

## 📌 Projenin Amacı ve Özeti

Piyasadaki hazır uçuş kollarının (HOTAS) mekanik ve elektriksel prensiplerini anlamak, gömülü sistem mimarilerini gerçek zamanlı bir simülasyon ortamına bağlamak amacıyla tasarlanmıştır.

Sistem temel olarak şu döngüyle çalışır:
1. Kullanıcının kumanda kolu ve gaz kızağı hareketleri analog voltaj sinyallerine dönüşür.
2. STM32 Nucleo-F446RE kartı bu sinyalleri 12-bit çözünürlükle DMA üzerinden kesintisiz örnekler.
3. Ham veriler yazılımsal hareketli ortalama (moving average) filtresinden geçirilerek titreşimlerden temizlenir.
4. Temizlenen eksen verileri UART üzerinden 115200 baud hızında bilgisayara aktarılır.
5. Python köprü yazılımı bu veriyi karşılar, mekanik açı daralmalarını kalibre eder ve sanal joystick sürücüsüne (vJoy) 15-bit (0–32768) eksen komutu olarak enjekte eder.
6. War Thunder oyunu sistemi standart bir fiziksel USB uçuş kolu olarak tanır.

---

## 🛠️ Kullanılan Teknolojiler ve Sistem Mimarisi

* **Mikrodenetleyici:** STM32 Nucleo-F446RE (ARM Cortex-M4 @ 168 MHz)
* **Geliştirme Ortamı:** STM32CubeIDE & STM32CubeMX
* **Gömülü Sürücüler:** STM32 HAL (Hardware Abstraction Layer), DMA, ADC, UART
* **Sinyal İşleme:** 8 örnekli dairesel hareketli ortalama filtresi (Moving Average Filter)
* **Ara Katman / Köprü:** Python 3 (`pyserial`, `pyvjoy`)
* **Sanal Giriş Sürücüsü:** vJoy Device Driver (Virtual Joystick API)
* **Hedef Simülasyon:** War Thunder (Gerçekçi / Tam Gerçekçi Kontroller)

---

## 🔌 Donanım Kurulumu ve Pin Bağlantı Tablosu

Sistemde iki adet döner potansiyometre (Roll ve Pitch için) ve bir adet sürgülü/lineer potansiyometre (Gaz kolu için) kullanılmıştır.

> **Önemli Donanım Notu:** STM32 dahili ADC referansı 3.3V seviyesindedir. Potansiyometrelerin VCC bacaklarına kesinlikle 5V verilmemeli, doğrudan kartın **3V3** pini kullanılmalıdır.

| Eksen / Fonksiyon | Fiziksel Giriş Elemanı | Nucleo Pini | CubeMX Fonksiyonu | Çözünürlük / Aralık |
| :--- | :--- | :--- | :--- | :--- |
| **Roll (Yatış - X)** | Döner Potansiyometre | **PA0 (A0)** | `ADC1_IN0` | 12-bit (1500–2400 ham)* |
| **Pitch (Yunuslama - Y)**| Döner Potansiyometre | **PA1 (A1)** | `ADC1_IN1` | 12-bit (0–4000 ham) |
| **Throttle (Gaz - Z)** | Sürgülü Potansiyometre | **PA4 (A2)** | `ADC1_IN4` | 12-bit (0–4000 ham) |
| **Seri Haberleşme (TX)**| ST-LINK Virtual COM | **PA2** | `USART2_TX` | 115200 Baud, 8N1 |
| **Seri Haberleşme (RX)**| ST-LINK Virtual COM | **PA3** | `USART2_RX` | 115200 Baud, 8N1 |

*\*Roll eksenindeki mekanik kol tasarımı potansiyometrenin tüm dönüş açısını (300°) kullanmadığından, ~60°'lik hareket aralığı yazılımsal olarak tam skalaya genişletilmiştir.*

---

## 🧠 Gömülü Yazılım ve Çalışma Mantığı

### Çok Kanallı ADC ve DMA Yapılandırması
Kart üzerinde CPU'yu meşgul etmeden yüksek hızda örnekleme yapabilmek için **DMA (Doğrudan Bellek Erişimi)** kullanılmıştır:
* **Scan Conversion Mode:** Açık (3 kanal sırayla taranır: Rank 1 -> IN0, Rank 2 -> IN1, Rank 3 -> IN4).
* **Continuous Conversion Mode:** Açık (Örnekleme sürekli tekrarlanır).
* **DMA Settings:** `Circular` mod ve `Half Word` (16-bit veri genişliği) seçilerek veriler doğrudan RAM tamponuna yazılır.

## 🚀 Kurulum ve Çalıştırma

### 1. Önkoşullar
- [vJoy Virtual Joystick Driver](https://sourceforge.net/projects/vjoystick/)
- Python 3.8+
- Required libraries:
  ```bash
  pip install pyserial pyvjoy
