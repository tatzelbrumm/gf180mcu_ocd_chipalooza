run 2 (after Tim 2f18cd4 config.txt + slot 8 URL fix): 5 projects placed (slots 2,4,6,7,15).
final_gds/, prefill_gds/: xz chunks + gds_unpack.sh (see each MANIFEST.txt). cells.tsv: hashes of the final GDS.
fixes/: what was needed to place slots 7 and 15 and what is missing for the others. DRC/LVS of run 2 not finished when this was pushed.
results/: run 2 DRC (gf180mcu_ocd_chipalooza_final.lyrdb: 3159 violations, DRC took 12681 s) and LVS (comp_gf180mcu_ocd_chipalooza.out: "Netlists do not match", 28 mismatches, same as run 1; the LVS only sees the empty slot wrappers) plus their logs and the work journal. The DRC database is KLayout .lyrdb (open in KLayout: Tools > Marker Browser).
Tim summary: fixes/TIM_SUMMARY.md
