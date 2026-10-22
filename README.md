<p align="center">
  <img src="assets/logo.svg" alt="HexaMagDB" width="560">
</p>

<p align="center">
  A curated dataset of doped Ba and Sr M-type hexaferrites (BaFe<sub>12</sub>O<sub>19</sub>, SrFe<sub>12</sub>O<sub>19</sub>)<br>
  with composition, synthesis, lattice parameters and magnetic properties extracted from the literature.
</p>

---

## Contents

| Path | Description |
| --- | --- |
| `data/hexamagdb.csv` | The dataset: 3,034 records from 505 publications |
| `streamlit_app.py` | Streamlit app to browse, filter, plot and download the data |

Each record is one sample from one publication. Main fields:

- **Composition:** `Formula`, `Dopant`, `Dopant_Amount`, `Substitution`
- **Synthesis:** `Synthesis_Method`, `Annealing_Temperature_C`, `Annealing_Time_h`
- **Structure:** `a_A`, `c_A`, `V_A3`, `Crystallite_Size_nm`, `Phase_Purity`, `Secondary_Phases`
- **Magnetism:** `Ms_emu_g`, `Mr_emu_g`, `Hc_kOe`, `Mr_Ms`, `Tc_K`, `Measurement_Temperature_K`, `Maximum_Field_kOe`
- **Provenance:** `DOI`, `Journal`, `Year`, `Comment`

Values are converted to common units. Values as printed by the authors are kept in the `*_Reported` columns.
Only isotropic polycrystalline powders and ceramics are included.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Status

Preliminary version. The data descriptor is in preparation. Please contact the authors before reusing the data.
