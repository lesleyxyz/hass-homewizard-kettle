[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
# hass-homewizard-kitchen

This HomeAssistant integration/custom_component connects to your HomeWizard Kitchen's account to control your HomeWizard Kitchen's Kettle.
Tested on a HomeWizard Kettle 1.4,HWK-KTL 1.07

Based on the pip module [homewizard-kitchen](https://github.com/lesleyxyz/python-homewizard-kitchen)

# Support
- ✅ Config Flow
- ✅ Water Heater (Current Temperature, Target Temperature)
- ✅ Sensor (Current Temperature, Target Temperature)
- ✅ Number Input (Target Temperature, Keep Warm Time)
- ✅ Switch (On/Off, Keep Warm, Boil Before Target)

# Installation
## Add to HACS
1. Install from HACS, add this repository as custom repository
2. Search into HACS store this integration and install
3. Full restart of home assistant is recomended

## Configure your device
1. Goto the HomeAssistant Integration page and click "Add Integration"
2. Search for "HomeWizard Kitchen Kettle"
3. Enter your HomeWizard Kitchen credentials
4. Select your Kettle & click done