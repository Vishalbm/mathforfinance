/ KDB+/q and Tickerplant Architecture for Tick Data
/ Post: https://mathforfinance.com/kdb-q-and-tickerplant-architecture-for-tick-data/
/ Code snippets from the post, in the order they appear.

/ ---- Snippet 1 ----
/ an empty trade table with typed columns
trade:([] time:`timestamp$(); sym:`symbol$(); price:`float$(); size:`long$())

/ ---- Snippet 2 ----
select vwap:size wavg price, volume:sum size by sym from trade where date=2026.10.23

/ ---- Snippet 3 ----
select open:first price, high:max price, low:min price, close:last price, volume:sum size
  by sym, bar:5 xbar time.minute
  from trade where date=2026.10.23

/ ---- Snippet 4 ----
update mid:0.5*bid+ask, spread:ask-bid from quote

/ ---- Snippet 5 ----
aj[`sym`time; trade; quote]
