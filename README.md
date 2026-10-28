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
| `data/hexamagdb.csv` | The dataset: 4,158 records from 610 publications |
| `streamlit_app.py` | Streamlit app to browse, filter, plot and download the data |

Each record is one sample from one publication. Main fields:

- **Composition:** `Formula`, `Dopant`, `Dopant_Amount`, `Substitution`
- **Synthesis:** `Synthesis_Method`, `Synthesis_Procedure`, `Synthesis_Notes`, `Calcination_Temperature_C`, `Calcination_Time_h`, `Sintering_Temperature_C`, `Sintering_Time_h`
- **Structure:** `a_A`, `c_A`, `V_A3`, `Crystallite_Size_nm`, `Particle_Size_nm`, `Particle_Size_Method`, `Phase_Purity`, `Secondary_Phases`, `Secondary_Phase_wt`
- **Magnetism:** `Ms_emu_g`, `Mr_emu_g`, `Hc_kOe`, `Mr_Ms`, `Ha_kOe`, `K_erg_cm3`, `K_erg_g`, `Tc_K`, `Measurement_Temperature_K`, `Ms_Determination_Method`, `Maximum_Field_kOe`
- **Provenance:** `DOI`, `Journal`, `Year`, `Comment`

Values are converted to common units. The synthesis as described by the authors is kept in `Synthesis_Procedure`.
Only isotropic polycrystalline powders and ceramics are included.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Status

Preliminary version. The data descriptor is in preparation. Please contact the authors before reusing the data.
