import time
import requests
import pandas as pd
import streamlit as st
from collections import Counter

st.set_page_config(page_title="Tes WHO GHO", layout="wide")
st.title("Tes struktur API WHO GHO (Indonesia)")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://ghoapi.azureedge.net/api"

KODE_FILE = [
    ("WHOSIS_000001", "Life expectancy at birth"), ("WHOSIS_000002", "HALE at birth"),
    ("WHOSIS_000015", "Life expectancy at age 60"), ("NCDMORT3070", "Prob. dying 30-70 NCD"),
    ("WHOSIS_000007", "Adult mortality rate"), ("WHOSIS_000004", "Crude death rate"),
    ("MDG_0000000007", "Under-five mortality"), ("MDG_0000000001", "Infant mortality"),
    ("WHOSIS_000003", "Neonatal mortality"), ("MDG_0000000026", "Maternal mortality ratio"),
    ("MDG_0000000025", "Births attended by skilled staff"), ("M_03", "Adolescent birth rate"),
    ("NUTRITION_STUNTING_PREV", "Stunting"), ("NUTRITION_WASTING_PREV", "Wasting"),
    ("NUTRITION_OVERWEIGHT_PREV", "Overweight children"), ("NUTRITION_ANEMIA_CHILDREN", "Anemia children"),
    ("NUTRITION_ANEMIA_WOMEN", "Anemia women"), ("WHS3_62", "MCV1 coverage"),
    ("WHS3_49", "Polio Pol3 coverage"), ("WHS3_40", "DTP3 coverage"),
    ("MDG_0000000020", "TB incidence"), ("MDG_0000000018", "TB prevalence"),
    ("HWF_0001", "Medical doctors"), ("HWF_0002", "Nursing and midwifery"),
    ("HWF_0003", "Pharmacists"), ("HWF_BE_HOSP", "Hospital beds"),
    ("UHC_INDEX_REPORTED", "UHC service coverage index"), ("WSH_WATER_SAFELY_MANAGED", "Safe drinking water"),
    ("WSH_SANITATION_SAFELY_MANAGED", "Safe sanitation"), ("NCD_BMI_30A", "Obesity adults"),
]
SAMPEL = ["WHOSIS_000001", "WHOSIS_000002", "MDG_0000000026", "MDG_0000000007",
          "NCD_BMI_30A", "UHC_INDEX_REPORTED", "WSH_WATER_SAFELY_MANAGED", "NCDMORT3070"]
KATA = ["stunting", "wasting", "overweight", "anaemia", "measles", "DTP3", "polio", "hospital beds",
        "nursing", "pharmac", "adolescent birth", "tuberculosis", "adult mortality", "crude death"]

def get(path, **params):
    return requests.get(f"{BASE}/{path}", params=params or None, headers=H, timeout=60)

if st.button("Jalankan tes", type="primary"):
    st.header("A. Katalog indikator")
    r = get("Indicator")
    st.write(f"HTTP **{r.status_code}** | {len(r.content):,} byte")
    js = r.json()
    items = js.get("value", [])
    st.write("Kunci respons:", list(js.keys()))
    st.write(f"Jumlah indikator: **{len(items)}** | kunci satu entri: {list(items[0].keys()) if items else '-'}")
    nama = {x.get("IndicatorCode"): x.get("IndicatorName") for x in items}

    st.header("B. Verifikasi kode yang ada di file")
    st.dataframe(pd.DataFrame([{"kode": k, "label_di_file": l, "nama_resmi_di_API": nama.get(k, "TIDAK ADA")}
                               for k, l in KODE_FILE]), use_container_width=True)

    st.header("C. Pencarian kata kunci pada nama resmi")
    for kt in KATA:
        cocok = [(c, n) for c, n in nama.items() if n and kt.lower() in n.lower()]
        st.write(f"**{kt}**: {len(cocok)} cocok")
        for c, n in cocok[:5]:
            st.text(f"  {c} | {n[:110]}")

    st.header("D. Baris Indonesia untuk sampel kode")
    for kode in SAMPEL:
        rr = get(kode, **{"$filter": "SpatialDim eq 'IDN'"})
        js = rr.json() if rr.status_code == 200 else {}
        rows = js.get("value", [])
        tahun = Counter(x.get("TimeDim") for x in rows)
        st.text(f"{kode}: HTTP {rr.status_code} | baris {len(rows)} | tahun unik {len(tahun)} | "
                f"maks baris per tahun {max(tahun.values()) if tahun else 0} | nextLink: {'@odata.nextLink' in js}")
        if rows:
            st.text("  SpatialDimType: " + str(dict(Counter(x.get("SpatialDimType") for x in rows)))
                    + " | TimeDimType: " + str(dict(Counter(x.get("TimeDimType") for x in rows))))
            for d in ("Dim1", "Dim2", "Dim3"):
                st.text(f"  {d}: tipe={dict(Counter(x.get(d + 'Type') for x in rows))} | "
                        f"nilai={dict(Counter(x.get(d) for x in rows).most_common(6))}")
            st.text("  kolom: " + ", ".join(rows[0].keys()))
            st.text("  contoh: " + str({k: rows[0].get(k) for k in ("TimeDim", "Value", "NumericValue", "Low", "High")}))
        time.sleep(1)
