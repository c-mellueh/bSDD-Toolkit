import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import de from "./locales/de.json";
import { useSettings } from "./state/settings";

// English strings are used as keys; missing German translations fall back to English.
i18n.use(initReactI18next).init({
  resources: { de: { translation: de }, en: { translation: {} } },
  lng: useSettings.getState().language,
  fallbackLng: false,
  keySeparator: false,
  nsSeparator: false,
  interpolation: { escapeValue: false },
  returnEmptyString: false,
});

useSettings.subscribe((s) => {
  if (i18n.language !== s.language) i18n.changeLanguage(s.language);
});

export default i18n;
