// gf180_cm_io: placeholder custom pads; port directions as seen from the pad.
// scripts/parse_config.py reads this file for the core-side pins of each pad type.

module gf180_cm_io__asig_in (DVDD, DVSS, VDD, VSS, pad, outp, outn, vcm, vref, iref, en_3v3, en_3v3_b);
    inout DVDD;
    inout DVSS;
    inout VDD;
    inout VSS;
    inout pad;
    output outp;
    output outn;
    input vcm;
    input vref;
    inout iref;
    input en_3v3;
    input en_3v3_b;
endmodule

module gf180_cm_io__asig_out (DVDD, DVSS, VDD, VSS, pad, vinp, vinn, vref, iref, en_3v3, en_3v3_b);
    inout DVDD;
    inout DVSS;
    inout VDD;
    inout VSS;
    inout pad;
    input vinp;
    input vinn;
    input vref;
    inout iref;
    input en_3v3;
    input en_3v3_b;
endmodule
