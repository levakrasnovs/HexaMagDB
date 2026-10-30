<p align="center">
  <img src="assets/logo.svg" alt="HexaMagDB" width="560">
</p>

<p align="center">
  A curated dataset of doped Ba and Sr M-type hexaferrites (BaFe<sub>12</sub>O<sub>19</sub>, SrFe<sub>12</sub>O<sub>19</sub>)<br>
  with composition, synthesis, lattice parameters and magnetic properties extracted from the literature.
</p>

Visit our demo <https://hexamagdb.streamlit.app/>.

Download HexaMagDB: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23807416.svg)](https://doi.org/10.5281/zenodo.23807416)

---

## Contents

| Path | Description |
| --- | --- |
| `data/hexamagdb.csv` | The dataset: 4,388 records from 662 publications |
| `Code_for_paper.ipynb` | Checks used for the technical validation of the dataset |
| `streamlit_app.py` | Streamlit app to browse, filter, plot and download the data |

HexaMagDB contains 4388 records of magnetic properties, structure and synthesis of polycrystalline Ba, Sr and mixed Ba–Sr M-type hexaferrites (AFe<sub>12</sub>O<sub>19</sub>), undoped and doped with 48 elements (Al, Bi, Ca, Cd, Ce, Co, Cr, Cu, Dy, Er, Eu, Ga, Gd, Hf, Ho, In, Ir, K, La, Li, Lu, Mg, Mn, Mo, Na, Nb, Nd, Ni, Pb, Pr, Re, Ru, Sb, Sc, Si, Sm, Sn, Ta, Tb, Ti, Tl, Tm, V, W, Y, Yb, Zn and Zr), covering 2095 unique compositions reported in 662 literature papers from 1986 to 2026. Single crystals, films and field-oriented or textured samples are not included. Every record contains at least one magnetic value.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Citation

Please cite the dataset as:

Khvashchevskaya, Y., Krasnov, L. & Popkov, V. **HexaMagDB: a dataset of magnetic properties, structure and synthesis of doped barium and strontium M-type hexaferrites.** Zenodo (2026). https://doi.org/10.5281/zenodo.23807416
