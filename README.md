# Calculadora de Classificació - Tira Voleibol Femení Catalunya

## Per què existeix aquest programa?

Es classifiquen **els 40 primers equips de 99 per promoció**. Els equips restants juguen un altre tipus de competició.

Mirar manualment la posició del nostre equip a la classificació de la tira és molt complicat perquè cal:

1. Creuar les dades de **Juvenil i Cadet** de cada club
2. Agrupar equips de **múltiples grups** amb diferent nombre de partits
3. Calcular la ponderació correctament
4. Ordenar els 99 equips segons els criteris oficials

Aquest programa automatitza tot el procés i mostra la classificació real de la tira.

## D'on surten les dades?

Totes les dades es recullen automàticament de la Federació Catalana de Voleibol:

🔗 [Classificacions oficials fcvolei.cat](https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1977&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=178&id_competicion=568)

## El Problema de la Ponderació

### La normativa diu:

> S'ordena per: **punts de la tira** → partits guanyats → diferència sets → diferència punts → resultats partits directes

Però **no especifica com es ponderen** els equips quan no juguen el mateix nombre de partits.

### Exemple del problema:

```
Equip A (grup de 8 equips):
  - 15 punts de 21 possibles (7 partits × 3 punts)
  - 15/21 = 71.4% dels punts possibles

Equip B (grup de 7 equips):
  - 14 punts de 18 possibles (6 partits × 3 punts)
  - 14/18 = 77.8% dels punts possibles

Qui va primer? 🤔
  - Si ordenem per punts absoluts: Equip A (15 > 14)
  - Si ordenem per percentatge: Equip B (77.8% > 71.4%)
```

**La federació no especifica la fórmula exacta de ponderació.**

## Com ho resol aquest programa?

Utilitzem el **percentatge de punts** com a criteri principal:

```
% Punts = (Punts obtinguts × 100) / (Total de partits del grup × 3)
```

**Ordre de classificació:**
1. **% de Punts** (de més a menys)
2. En cas d'empat → **Partits guanyats** (de més a menys)
3. En cas d'empat → **Diferència de sets** (de més a menys)
4. En cas d'empat → **Diferència de punts** (de més a menys)

⚠️ **IMPORTANT:** El programa **NO** té en compte els resultats de partits directes (última regla de desempat) perquè requereix analitzar cada partit individualment.

---

**Objectiu:** Saber si estem entre els 40 primers i ens classifiquem per promoció! 🏐

Si detectes que l'ordre no coincideix amb la classificació oficial, probablement la federació utilitza una fórmula de ponderació diferent. En aquest cas, caldria contactar-los per conèixer la fórmula exacta.

## Com executar el programa

Per executar el programa principal:

```bash
uv sync
uv run scraper
```

