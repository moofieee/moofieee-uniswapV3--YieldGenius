---
title: Stablecoins Daily
sources:
  - summary_stats_protocol_stable_count: kpis/summary_stats_protocol_stable_count.sql
  - stablecoin_count_by_lauch_date: kpis/stablecoin_count_by_lauch_date.sql
---

### Stablecoins Market

<BigValue
data={stablecoin_count_by_lauch_date}
title='Total Stablecoin lauched till date'
value='total_stablecoins'
maxWidth='20'
/>

<DataTable data={stablecoin_count_by_lauch_date} rowLines="false">
  <Column id="peg_mechanism" />
  <Column id="stablecoins" />
  <Column id="days_since_last_lauch" />
</DataTable>

The above table show protocol count for given number of Stablecoins they launched.

### Peg Analysis

- Protocols off pegs
  - When was last time peg went off
  - Total number of peg off
  - peg off by category
