# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Public data repository for **ENSIN 2015** (Encuesta Nacional de la Situación Nutricional en Colombia 2015 — Colombian National Nutritional Survey). Used for medical research and teaching at CUC. Contains approximately 1.77 million records across 18 relational tables, available in SQL Server and Stata formats.

## Database setup (SQL Server)

To restore the database from backup:
```sql
RESTORE DATABASE ENSIN_2015 FROM DISK = 'SQL_Server/Copia/Copia_Ensin_2015_Pública.bak'
```

To create the schema and bulk-load flat files:
```
SQL_Server/Sintaxis/Crear_Ensin_2015_Pública.sql
```
The flat files are pipe/tab-delimited `.TXT` files under `SQL_Server/Datos_Planos/`.

## Data formats

| Format | Location | Notes |
|--------|----------|-------|
| SQL Server flat files | `SQL_Server/Datos_Planos/*.TXT` | Tab-separated |
| SQL Server backup | `SQL_Server/Copia/*.bak` | 1.2 GB |
| Stata | `Formato_Stata/*.dta` | R24.dta is 815 MB |

## Key tables and their contents

| Table (SQL) / File | Records | Description |
|--------------------|---------|-------------|
| `R24` | 782,492 | 24-hour dietary recall — largest table |
| `ANTR` (ANTROPOMETRIA) | 137,579 | Anthropometric measurements |
| `SA_3` | 129,188 | Household socioeconomic data |
| `PISNSP` | 28,902 | Food security / nutrition practices |
| `AF_ADULTOS` | 17,943 | Adults — food consumption |
| `AF_ADOLESCENTES` | 6,769 | Adolescents — food consumption |

Age-group tables (`AF_PREESCOLARES`, `AF_ESCOLARES`, `AF_ADOLESCENTES`, `AF_ADULTOS`, `AF_GESTANTES`, `AF_A_GESTANTES`) share a common structure with food frequency and anthropometric indicators per demographic group.

## Anthropometric Z-scores (`ANTR` table)

`ANTR` has no header row in its flat file (`SQL_Server/Datos_Planos/Hogar_Antrop.TXT`) — column order comes from the `CREATE TABLE [dbo].[ANTR]` statement in `Crear_Ensin_2015_Pública.sql`. Relevant raw and derived fields:

| Column | Meaning |
|--------|---------|
| `ANTSEXO` | Sex |
| `AN_EDAD` / `AN_EDADM` | Age in years / months |
| `AN_7` | Weight (kg) |
| `AN_8` | Height/length (cm) |
| `AN_9` | Waist circumference (cm) |
| `AN_IMC` | BMI |
| `WHZ` | Weight-for-height Z-score |
| `WAZ` | Weight-for-age Z-score |
| `HAZ` | Height/length-for-age Z-score |
| `BAZ` | BMI-for-age Z-score |
| `flagAnthro` | Plausibility flags for WHZ/WAZ/HAZ, computed via WHO Anthro (ages 0–5) |
| `flagPlus` | Plausibility flags for BAZ, computed via WHO AnthroPlus (ages 5–19) |

Derived nutritional-status categories built from these Z-scores also live in `ANTR`: `retrasoTalla` (stunting), `desnutricionGlobal` (underweight), `desnutricionAguda`/`desnutricionAgudaSev` (wasting), `tallaBaja1/2`, `pesoBajo1/2`, `estadoImc1`–`estadoImc9` (BMI status categories), `obesidadAbdominal`.

## Common key fields

- `LLAVE_HOGAR` — household identifier (joins household-level tables)
- `LLAVE_PERSONA` — individual identifier (primary key across most tables)
- `FactorExpansión` — survey expansion weight; **always apply when computing population-level estimates**
- `Región` / `Subregión` — geographic stratification
- `wealth_index` / `cuartil_riqueza` — wealth index and quartile

## Documentation

- `Dic_Ensin_Pública20052021.xlsx` — variable dictionary with codes and labels (covers 2005–2021 evolution)
- `Modelo_ER_Ensin_Anonimizada_Pública.pdf` — entity-relationship diagram
- `Doc_Relacional_Base_Datos_ENSIN_Pública.docx` — relational model documentation
- `libro-ensin-2015.pdf` — full ENSIN 2015 survey report (56 MB)

## Statistical analysis notes

- Survey uses stratified complex sampling; expansion factors must be used for any prevalence/mean estimates.
- Stata `.dta` files are ready for use with `svyset` and `svy:` prefix commands.
- For R, use the `survey` package with `LLAVE_HOGAR` as the PSU and `FactorExpansión` as the weight.
