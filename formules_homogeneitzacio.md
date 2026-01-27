# Fórmules d'Homogeneïtzació per la Tira

## Context Real

**Situació:**
- Grups de 7 equips: 6 partits per equip
- Grups de 8 equips: 7 partits per equip  
- **Al final de la fase**: Tots hauran jugat tots els seus partits
- **Durant la fase**: Pot haver-hi desfasaments temporals
- **Partits no jugats**: Federació comptabilitza 0-0 (ambdós equips perden)

## Per què aquest document?

L'objectiu principal d'aquesta anàlisi és disposar d'una referència interna per saber **en quina zona de la classificació ens movem realment**.

Davant la incertesa del criteri que aplicarà la federació per barrejar grups de 7 i 8 equips, he desenvolupat diverses fórmules per les següents raons:

* **Mesurar l'impacte real**: He comprovat que, depenent de la fórmula que s'esculli, el nostre equip pot ballar entre la **13a i la 17a posició**.
* **Consciència de la variabilitat**: Queda clar que la fórmula que apliqui la federació serà determinant, però també que qualsevol mètode triat acabarà beneficiant uns equips i perjudicant-ne uns altres inevitablement.
* **Seguiment propi**: Com que falten 2 partits per acabar i les dades encara són incompletes, aquestes fórmules m'ajuden a tenir una idea de "per on anem" sense dependre d'una única classificació oficial que pot ser enganyosa.

---

## Efecte Real de Grup Petit vs Gran

### Matemàtica pura:

**Grup 7 (6 partits):**
- Cada partit = 16.7% del total (1/6)
- Victòria: +16.7%
- Derrota: +0%
- **Variació per partit**: ±16.7%

**Grup 8 (7 partits):**
- Cada partit = 14.3% del total (1/7)
- Victòria: +14.3%
- Derrota: +0%
- **Variació per partit**: ±14.3%

### Què vol dir això?

**Grup petit (7 equips):**
- ✅ Més fàcil pujar ràpid (menys partits per recuperar)
- ❌ Més fàcil baixar ràpid (menys marge d'error)
- Cada partit pesa MÉS

**Grup gran (8 equips):**
- ✅ Més estable (canvis graduals)
- ❌ Més lent recuperar-se (més partits per compensar)
- Cada partit pesa MENYS

**Conclusió neutral**: No és millor ni pitjor, és **diferent**
- Grup petit = Alta variància = Més volàtil
- Grup gran = Baixa variància = Més estable

---

## Cas Extrem: Partits No Jugats

**Problema real**: Equip amb partit ajornat

**Equip A** (grup 8, 6 de 7 partits jugats):
- 15 punts en 6 partits = 15/18 = 83.3%
- Li falta 1 partit

**Equip B** (grup 7, 6 de 6 partits jugats):
- 13 punts en 6 partits = 13/18 = 72.2%
- Ho ha jugat tot

### Amb fórmula actual:
- Equip A: 83.3% (però li falta 1 partit)
- Equip B: 72.2% (dades completes)
- **Ordre**: A > B

### Si A perd el partit pendent:
- Equip A: 15/21 = 71.4%
- Equip B: 72.2%
- **Ordre**: B > A

**Problema**: Durant la fase, A està per sobre amb dades incompletes.

---

## Fórmula Actual (Implementada)

```python
points_percentage = (total_points / (matches_played * 3)) * 100
```

**Què fa:**
- Calcula % de punts aconseguits sobre punts jugats
- NO extrapola partits pendents

**Pros:**
- ✅ Dades 100% reals (cap suposició)
- ✅ Reflecteix rendiment exacte fins ara
- ✅ Simple i transparent

**Contres:**
- ❌ Equips amb partits pendents poden estar inflats
- ❌ No comparable directament entre grups diferents
- ❌ Durant la fase pot canviar molt

**Quan usar-la:**
- Al **final de la fase** (tots amb dades completes)
- Per veure rendiment **real** fins ara

---

## Alternativa 1: Projectar a Total de Partits del Grup

```python
def project_to_group_total(total_points, matches_played, group_size):
    total_matches_in_group = group_size - 1
    if matches_played == 0:
        return 0
    
    # Projectar a tots els partits del grup
    projected_points = (total_points / matches_played) * total_matches_in_group
    max_points = total_matches_in_group * 3
    points_percentage = (projected_points / max_points) * 100
    
    return points_percentage, projected_points
```

**Exemple:**
- Equip A (grup 8, 6 partits jugats, 15 punts):
  - Projectat: 15/6 × 7 = 17.5 punts
  - Percentatge: 17.5/21 = 83.3%
  
- Equip B (grup 7, 6 partits jugats, 13 punts):
  - Projectat: 13/6 × 6 = 13 punts
  - Percentatge: 13/18 = 72.2%

**Pros:**
- ✅ Cada equip es compara amb el seu grup complet
- ✅ Projecta els partits pendents
- ✅ Manté proporció de rendiment

**Contres:**
- ❌ Assumeix rendiment constant (pot no ser cert)
- ❌ Encara compara % sobre diferents bases (18 vs 21)
- ❌ Un bon inici domina la projecció

---

## Alternativa 2: Normalitzar TOTS a 7 Partits

```python
def normalize_all_to_7(total_points, matches_played):
    if matches_played == 0:
        return 0
    
    # Projectar tots a 7 partits
    projected_points = (total_points / matches_played) * 7
    points_percentage = (projected_points / 21) * 100
    
    return points_percentage, projected_points
```

**Exemple:**
- Equip A (grup 8, 6 partits, 15 punts):
  - Projectat: 15/6 × 7 = 17.5 punts → 83.3%
  
- Equip B (grup 7, 6 partits, 13 punts):
  - Projectat: 13/6 × 7 = 15.2 punts → 72.4%

**Pros:**
- ✅ TOTS es comparen sobre la mateixa base (21 punts)
- ✅ Directament comparable
- ✅ Fàcil d'entendre

**Contres:**
- ❌ Grup 8 sempre projecta 1 partit menys del total
- ❌ Grup 7 projecta 1 partit més si no està complet
- ❌ Al final de fase, grups de 8 estan normalitzats (7 de 7), grups de 7 no (6 de 7)

**⚠️ Problema al final de fase:**
Quan tots han acabat:
- Grup 8: Ha jugat 7 → normalitzat a 7 → sense projecció ✅
- Grup 7: Ha jugat 6 → normalitzat a 7 → projecta 1 partit ❌

**Això vol dir que aquesta fórmula sempre beneficia/perjudica segons el grup!**

---

## Alternativa 3: Normalitzar a MÍNIM (6 partits)

```python
def normalize_all_to_min(total_points, matches_played):
    if matches_played == 0:
        return 0
    
    # Projectar tots a 6 partits
    projected_points = (total_points / matches_played) * 6
    points_percentage = (projected_points / 18) * 100
    
    return points_percentage, projected_points
```

**Exemple:**
- Equip A (grup 8, 7 partits, 15 punts):
  - Projectat: 15/7 × 6 = 12.9 punts → 71.4%
  
- Equip B (grup 7, 6 partits, 13 punts):
  - Projectat: 13/6 × 6 = 13 punts → 72.2%

**Pros:**
- ✅ TOTS comparables sobre 18 punts
- ✅ Al final de fase: grup 7 sense projecció, grup 8 normalitzat ✅
- ✅ Simètric amb Alternativa 2

**Contres:**
- ❌ Grup 8 sempre "perd" 1 partit en la comparació
- ❌ Projecta enrere en lloc d'endavant (menys intuïtiu)

---

## Alternativa 4: Ponderar per Partits Jugats

```python
def weighted_by_completion(total_points, matches_played, group_size):
    total_group_matches = group_size - 1
    if matches_played == 0:
        return 0
    
    # Percentatge sobre partits jugats
    base_percentage = (total_points / (matches_played * 3)) * 100
    
    # Factor de completesa
    completion_ratio = matches_played / total_group_matches
    
    # Ajustar percentatge
    # Si has jugat tot: factor = 1.0 (sense ajust)
    # Si has jugat meitat: factor = 0.85 (lleu ajust)
    adjustment_factor = 0.7 + 0.3 * completion_ratio
    
    adjusted_percentage = base_percentage * adjustment_factor
    
    return adjusted_percentage
```

**Exemple:**
- Equip A (grup 8, 6 de 7 partits, 15 punts):
  - Base: 15/18 = 83.3%
  - Completesa: 6/7 = 0.857
  - Ajust: 0.7 + 0.3×0.857 = 0.957
  - Final: 83.3% × 0.957 = 79.7%
  
- Equip B (grup 7, 6 de 6 partits, 13 punts):
  - Base: 13/18 = 72.2%
  - Completesa: 6/6 = 1.0
  - Ajust: 0.7 + 0.3×1.0 = 1.0
  - Final: 72.2% × 1.0 = 72.2%

**Pros:**
- ✅ Penalitza equips amb partits pendents
- ✅ Al final de fase tots tenen factor 1.0 (sense ajust)
- ✅ Reconeix que menys dades = menys certesa

**Contres:**
- ❌ L'ajust (0.7 + 0.3×) és arbitrari
- ❌ Redueix percentatges d'equips amb partits pendents
- ❌ Si un grup va més endarrerit, tots els seus equips es penalitzen

---

## Comparativa Realista: Durant la Fase

### Cas: Un equip amb partit pendent

**Equip A** (grup 8, 6 de 7 partits):
- 5V-1D, 15 punts

**Equip B** (grup 7, 6 de 6 partits):
- 4V-2D, 12 punts

| Fórmula | Equip A | Equip B | Ordre |
|---------|---------|---------|-------|
| Actual | 83.3% | 66.7% | A >> B |
| Projectar a total grup | 83.3% | 66.7% | A >> B |
| Normalitzar a 7 | 87.5% | 70.0% | A >> B |
| Normalitzar a 6 | 75.0% | 66.7% | A > B |
| Ponderar completesa | 79.7% | 66.7% | A > B |

**Al jugar el partit pendent, si A perd:**
- A: 15 punts / 21 = 71.4%
- B: 66.7%
- **Ordre final**: A > B (encara guanya)

---

## Comparativa Realista: Final de Fase

### Tots els partits jugats

**Equip A** (grup 8, 7 partits):
- 5V-2D, 15 punts, 71.4%

**Equip B** (grup 7, 6 partits):
- 4V-2D, 12 punts, 66.7%

| Fórmula | Equip A | Equip B | Diferència |
|---------|---------|---------|------------|
| Actual | 71.4% | 66.7% | 4.7% |
| Projectar a total | 71.4% | 66.7% | 4.7% |
| Normalitzar a 7 | 71.4% | 70.0% | 1.4% ⚠️ |
| Normalitzar a 6 | 64.3% | 66.7% | -2.4% ⚠️ |
| Ponderar completesa | 71.4% | 66.7% | 4.7% |

**⚠️ Observació crítica:**
- Normalitzar a 7: Sempre projecta 1 partit extra a grups de 7 (beneficia)
- Normalitzar a 6: Sempre descarta 1 partit de grups de 8 (perjudica)

**Conclusió**: Normalitzar SEMPRE beneficia/perjudica segons el grup!

---

## La Realitat Matemàtica

### No pots normalitzar sense beneficiar a algú

Si normalitzes a X partits:
- Grups amb > X partits: se'ls descarten dades reals
- Grups amb < X partits: se'ls projecten dades futures

**No hi ha punt neutre** si els grups tenen diferent nombre de partits.

### Opcions reals:

**Opció A**: No normalitzar (actual)
- Grups petits: més volatilitat
- Grups grans: més estabilitat
- **Efecte**: Cap (és matemàticament neutre)

**Opció B**: Normalitzar a 7
- Grups petits (+1 partit): projecta futur
- Grups grans (0 partits): dades reals
- **Efecte**: Beneficia grups petits amb bon inici

**Opció C**: Normalitzar a 6
- Grups petits (0 partits): dades reals
- Grups grans (-1 partit): descarta dades
- **Efecte**: Perjudica grups grans

**Opció D**: Ponderar per completesa
- Penalitza partits pendents
- Al final de fase: neutre
- **Efecte**: Durant fase, penalitza desfasaments

---

## Recomanació Final

### Per DURANT la fase:

Si vols saber posició aproximada amb partits pendents:
→ **Ponderar per completesa** (penalitza incomplets)

Si vols projectar com aniran:
→ **Normalitzar a 7** (optimista) o **a 6** (pessimista)

Si vols dades 100% reals:
→ **Actual** (sense projeccions)

### Per FINAL de fase:

**Fórmula Actual** és l'única neutral perquè:
- Tots tenen dades completes
- Cap projecció necessària
- Cada equip comparat amb el seu màxim real

**PERÒ**: La volatilitat grup petit vs gran és real i inevitable.

La federació probablement usa l'actual al final, i per això el teu programa ja està bé! 🏐

---

## Conclusió Pràctica

Per la vostra filla no importa quina fórmula uses DURANT la fase, perquè:
1. Al final tots hauran jugat tots els partits
2. La classificació final serà amb dades completes
3. La volatilitat del grup petit és tant avantatge com desavantatge
