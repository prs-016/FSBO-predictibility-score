"""Demo fixture: interleaved home + visiting plays from real match data.

Visiting-team good receptions (aXXR# / aXXR+) are the prediction trigger.
Home-team attacks in Reception phase populate the prev_1..prev_5 history.
"""

DEMO_LINES: list[str] = [
    # ── Set 3, early points (home leading) ──────────────────────────────
    '*12S!~~~~7~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":88,"hs":1,"vs":0,"hsp":6,"vsp":1,"ph":"Serve","pd":1}',
    'a02R+~~~~5~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":88,"hs":1,"vs":0,"hsp":6,"vsp":1,"ph":"Reception","pd":1}',
    'a05E#~~~~~~4|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":88,"hs":1,"vs":0,"hsp":6,"vsp":1,"ph":"Reception","pd":1}',
    'a06A-X6~~2~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":88,"hs":1,"vs":0,"hsp":6,"vsp":1,"ph":"Reception","pd":1}',
    '*02B+~~~~~~4|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":88,"hs":1,"vs":0,"hsp":6,"vsp":1,"ph":"Reception","pd":1}',

    '*12S!~~~~7~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":89,"hs":2,"vs":0,"hsp":6,"vsp":1,"ph":"Serve","pd":2}',
    'a09R#~~~~1~5|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":89,"hs":2,"vs":0,"hsp":6,"vsp":1,"ph":"Reception","pd":2}',
    'a05E#KM~~~~4|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":89,"hs":2,"vs":0,"hsp":6,"vsp":1,"ph":"Reception","pd":2}',
    'a16A+X5~~4~1|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":89,"hs":2,"vs":0,"hsp":6,"vsp":1,"ph":"Reception","pd":2}',
    '*05D+~~~~4~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":89,"hs":2,"vs":0,"hsp":6,"vsp":1,"ph":"Transition","pd":2}',
    '*09E#~~~~~~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":89,"hs":2,"vs":0,"hsp":6,"vsp":1,"ph":"Transition","pd":2}',
    '*06A-V6~~2~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":89,"hs":2,"vs":0,"hsp":6,"vsp":1,"ph":"Transition","pd":2}',

    '*07S=~~~~7~1|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":91,"hs":3,"vs":1,"hsp":5,"vsp":6,"ph":"Serve","pd":2}',
    'a12R+~~~~5~5|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":91,"hs":3,"vs":1,"hsp":5,"vsp":6,"ph":"Reception","pd":2}',
    'a05E#K7~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":91,"hs":3,"vs":1,"hsp":5,"vsp":6,"ph":"Reception","pd":2}',
    'a15A#X7~~4~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":91,"hs":3,"vs":1,"hsp":5,"vsp":6,"ph":"Reception","pd":2}',
    '*09D#~~~~4~5|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":91,"hs":3,"vs":1,"hsp":5,"vsp":6,"ph":"Transition","pd":2}',

    '*06S-~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":93,"hs":4,"vs":2,"hsp":4,"vsp":5,"ph":"Serve","pd":2}',
    '*06S+~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":94,"hs":5,"vs":2,"hsp":4,"vsp":5,"ph":"Serve","pd":3}',
    '*06S+~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":95,"hs":6,"vs":2,"hsp":4,"vsp":5,"ph":"Serve","pd":4}',
    'a12F+~~~~7~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":95,"hs":6,"vs":2,"hsp":4,"vsp":5,"ph":"Transition","pd":4}',
    '*06S#~~~~1~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":96,"hs":7,"vs":2,"hsp":4,"vsp":5,"ph":"Serve","pd":5}',

    '*06S!~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":97,"hs":8,"vs":2,"hsp":4,"vsp":5,"ph":"Serve","pd":6}',
    'a04R+~~~~5~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":97,"hs":8,"vs":2,"hsp":4,"vsp":5,"ph":"Reception","pd":6}',
    'a05E#K1~~~~2|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":97,"hs":8,"vs":2,"hsp":4,"vsp":5,"ph":"Reception","pd":6}',
    'a16A#X5~~4~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":97,"hs":8,"vs":2,"hsp":4,"vsp":5,"ph":"Reception","pd":6}',
    '*02B!~~~~~~4|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":97,"hs":8,"vs":2,"hsp":4,"vsp":5,"ph":"Reception","pd":6}',
    '*06D=~~~~2~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":97,"hs":8,"vs":2,"hsp":4,"vsp":5,"ph":"Transition","pd":6}',

    '*04S=~~~~5~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":99,"hs":9,"vs":3,"hsp":3,"vsp":4,"ph":"Serve","pd":6}',
    'a16R+~~~~5~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":99,"hs":9,"vs":3,"hsp":3,"vsp":4,"ph":"Reception","pd":6}',
    'a05E#KM~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":99,"hs":9,"vs":3,"hsp":3,"vsp":4,"ph":"Reception","pd":6}',
    'a06A+X6~~2~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":99,"hs":9,"vs":3,"hsp":3,"vsp":4,"ph":"Reception","pd":6}',
    '*05D+~~~~2~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":99,"hs":9,"vs":3,"hsp":3,"vsp":4,"ph":"Transition","pd":6}',

    '*09S#~~~~5~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":101,"hs":10,"vs":4,"hsp":2,"vsp":3,"ph":"Serve","pd":6}',
    '*09S!~~~~7~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":102,"hs":11,"vs":4,"hsp":2,"vsp":3,"ph":"Serve","pd":7}',
    'a16R#~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":102,"hs":11,"vs":4,"hsp":2,"vsp":3,"ph":"Reception","pd":7}',
    'a05E#KB~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":102,"hs":11,"vs":4,"hsp":2,"vsp":3,"ph":"Reception","pd":7}',
    'a05A-PP~~3~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":102,"hs":11,"vs":4,"hsp":2,"vsp":3,"ph":"Reception","pd":7}',
    '*09S-~~~~7~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":103,"hs":11,"vs":5,"hsp":2,"vsp":2,"ph":"Serve","pd":6}',

    'a04R-~~~~1~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":104,"hs":11,"vs":6,"hsp":2,"vsp":2,"ph":"Reception","pd":5}',
    '*05E#K2~~~~4|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":104,"hs":11,"vs":6,"hsp":2,"vsp":2,"ph":"Reception","pd":5}',
    '*16A+X5~~4~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":104,"hs":11,"vs":6,"hsp":2,"vsp":2,"ph":"Reception","pd":5}',

    '*05S-~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":105,"hs":12,"vs":6,"hsp":1,"vsp":2,"ph":"Serve","pd":6}',
    '*05S#~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":106,"hs":13,"vs":6,"hsp":1,"vsp":2,"ph":"Serve","pd":7}',
    'a09R+~~~~5~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":106,"hs":13,"vs":6,"hsp":1,"vsp":2,"ph":"Reception","pd":7}',
    'a05E#K7~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":106,"hs":13,"vs":6,"hsp":1,"vsp":2,"ph":"Reception","pd":7}',
    'a16A#X5~~4~1|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":106,"hs":13,"vs":6,"hsp":1,"vsp":2,"ph":"Reception","pd":7}',

    '*05S-~~~~1~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":107,"hs":14,"vs":6,"hsp":1,"vsp":2,"ph":"Serve","pd":8}',
    '*05S+~~~~1~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":108,"hs":15,"vs":6,"hsp":1,"vsp":2,"ph":"Serve","pd":9}',
    'a04D+~~~~4~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":108,"hs":15,"vs":6,"hsp":1,"vsp":2,"ph":"Transition","pd":9}',
    '*09E#~~~~~~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":108,"hs":15,"vs":6,"hsp":1,"vsp":2,"ph":"Transition","pd":9}',
    '*16A+V5~~4~2|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":108,"hs":15,"vs":6,"hsp":1,"vsp":2,"ph":"Transition","pd":9}',

    '*05S/~~~~1~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":109,"hs":16,"vs":6,"hsp":1,"vsp":2,"ph":"Serve","pd":10}',
    'a16R+~~~~5~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":109,"hs":16,"vs":6,"hsp":1,"vsp":2,"ph":"Reception","pd":10}',
    'a05E#KM~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":109,"hs":16,"vs":6,"hsp":1,"vsp":2,"ph":"Reception","pd":10}',
    'a06A-X6~~2~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":109,"hs":16,"vs":6,"hsp":1,"vsp":2,"ph":"Reception","pd":10}',
    '*16A#~~~~4~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":109,"hs":16,"vs":6,"hsp":1,"vsp":2,"ph":"Transition","pd":10}',

    '*05S=~~~~1~1|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":110,"hs":17,"vs":6,"hsp":1,"vsp":2,"ph":"Serve","pd":11}',
    'a16R+~~~~5~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":111,"hs":17,"vs":7,"hsp":1,"vsp":1,"ph":"Reception","pd":10}',
    'a05E#KM~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":111,"hs":17,"vs":7,"hsp":1,"vsp":1,"ph":"Reception","pd":10}',
    'a06A-X6~~2~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":111,"hs":17,"vs":7,"hsp":1,"vsp":1,"ph":"Reception","pd":10}',
    '*16B=~~~~~~4|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":111,"hs":17,"vs":7,"hsp":1,"vsp":1,"ph":"Transition","pd":10}',

    'a16R-~~~~5~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":112,"hs":17,"vs":8,"hsp":1,"vsp":1,"ph":"Reception","pd":9}',
    'a09E#~~~~~~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":112,"hs":17,"vs":8,"hsp":1,"vsp":1,"ph":"Reception","pd":9}',
    'a16A+V5~~4~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":112,"hs":17,"vs":8,"hsp":1,"vsp":1,"ph":"Reception","pd":9}',
    '*09F+~~~~7~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":112,"hs":17,"vs":8,"hsp":1,"vsp":1,"ph":"Transition","pd":9}',
    '*05E#K7~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":112,"hs":17,"vs":8,"hsp":1,"vsp":1,"ph":"Transition","pd":9}',
    '*16A#X5~~4~1|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":112,"hs":17,"vs":8,"hsp":1,"vsp":1,"ph":"Transition","pd":9}',

    '*12S-~~~~7~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":113,"hs":18,"vs":8,"hsp":6,"vsp":1,"ph":"Serve","pd":10}',
    'a12R+~~~~5~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":113,"hs":18,"vs":8,"hsp":6,"vsp":1,"ph":"Reception","pd":10}',
    'a05E#K1~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":113,"hs":18,"vs":8,"hsp":6,"vsp":1,"ph":"Reception","pd":10}',
    'a15A#X2~~2~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":113,"hs":18,"vs":8,"hsp":6,"vsp":1,"ph":"Reception","pd":10}',
    '*07B=~~~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":113,"hs":18,"vs":8,"hsp":6,"vsp":1,"ph":"Reception","pd":10}',

    'a12R#~~~~5~1|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":114,"hs":18,"vs":9,"hsp":6,"vsp":6,"ph":"Reception","pd":9}',
    'a05E#K1~~~~2|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":114,"hs":18,"vs":9,"hsp":6,"vsp":6,"ph":"Reception","pd":9}',
    'a02A-X5~~4~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":114,"hs":18,"vs":9,"hsp":6,"vsp":6,"ph":"Reception","pd":9}',
    '*07S-~~~~7~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":115,"hs":19,"vs":9,"hsp":5,"vsp":6,"ph":"Serve","pd":10}',

    'a02R+~~~~5~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":118,"hs":20,"vs":11,"hsp":4,"vsp":4,"ph":"Reception","pd":9}',
    'a05E#KS~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":118,"hs":20,"vs":11,"hsp":4,"vsp":4,"ph":"Reception","pd":9}',
    'a06A-X8~~9~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":118,"hs":20,"vs":11,"hsp":4,"vsp":4,"ph":"Reception","pd":9}',
    '*15B#~~~~~~2|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":118,"hs":20,"vs":11,"hsp":4,"vsp":4,"ph":"Transition","pd":9}',
    '*06S-~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":117,"hs":20,"vs":10,"hsp":4,"vsp":5,"ph":"Serve","pd":10}',

    '*04S#~~~~5~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":119,"hs":21,"vs":11,"hsp":3,"vsp":4,"ph":"Serve","pd":10}',
    'a04R-~~~~1~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":121,"hs":22,"vs":12,"hsp":3,"vsp":3,"ph":"Reception","pd":10}',
    'a05E#KS~~~~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":121,"hs":22,"vs":12,"hsp":3,"vsp":3,"ph":"Reception","pd":10}',
    'a16A#X5~~4~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":121,"hs":22,"vs":12,"hsp":3,"vsp":3,"ph":"Reception","pd":10}',
    '*04S=~~~~5~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":120,"hs":22,"vs":11,"hsp":3,"vsp":4,"ph":"Serve","pd":11}',

    '*09S-~~~~7~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":122,"hs":23,"vs":12,"hsp":2,"vsp":3,"ph":"Serve","pd":11}',
    'a05D+~~~~2~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":122,"hs":23,"vs":12,"hsp":2,"vsp":3,"ph":"Transition","pd":11}',
    '*09E#~~~~~~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":122,"hs":23,"vs":12,"hsp":2,"vsp":3,"ph":"Transition","pd":11}',
    '*16A/V5~~4~1|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":122,"hs":23,"vs":12,"hsp":2,"vsp":3,"ph":"Transition","pd":11}',

    'a16R-~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":123,"hs":23,"vs":13,"hsp":2,"vsp":2,"ph":"Reception","pd":10}',
    'a05E#KM~~~~9|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":123,"hs":23,"vs":13,"hsp":2,"vsp":2,"ph":"Reception","pd":10}',
    'a16A=V5~~4~5|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":123,"hs":23,"vs":13,"hsp":2,"vsp":2,"ph":"Reception","pd":10}',
    '*05S-~~~~1~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":125,"hs":24,"vs":14,"hsp":1,"vsp":2,"ph":"Serve","pd":10}',

    'a16R#~~~~1~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":124,"hs":23,"vs":14,"hsp":2,"vsp":2,"ph":"Reception","pd":9}',
    'a05E#KB~~~~3|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":124,"hs":23,"vs":14,"hsp":2,"vsp":2,"ph":"Reception","pd":9}',
    'a05A-PP~~3~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":124,"hs":23,"vs":14,"hsp":2,"vsp":2,"ph":"Reception","pd":9}',
    '*09D=~~~~3~7|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":125,"hs":24,"vs":14,"hsp":1,"vsp":2,"ph":"Transition","pd":10}',

    'a04R+~~~~5~6|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":126,"hs":24,"vs":15,"hsp":1,"vsp":1,"ph":"Reception","pd":9}',
    'a05E#K1~~~~2|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":126,"hs":24,"vs":15,"hsp":1,"vsp":1,"ph":"Reception","pd":9}',
    'a16A#X5~~4~8|{"m":"05b080cd351318b4db44bac87b101af3","s":3,"p":126,"hs":24,"vs":15,"hsp":1,"vsp":1,"ph":"Reception","pd":9}',

    # ── Set 4 ────────────────────────────────────────────────────────────
    '*05S-~~~~9~6|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":127,"hs":0,"vs":0,"hsp":1,"vsp":1,"ph":"Serve","pd":0}',
    'a06R+~~~~5~2|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":127,"hs":0,"vs":0,"hsp":1,"vsp":1,"ph":"Reception","pd":0}',
    'a02E#~~~~~~9|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":127,"hs":0,"vs":0,"hsp":1,"vsp":1,"ph":"Reception","pd":0}',
    'a06A-V6~~2~6|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":127,"hs":0,"vs":0,"hsp":1,"vsp":1,"ph":"Reception","pd":0}',
    '*06B+~~~~~~2|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":127,"hs":0,"vs":0,"hsp":1,"vsp":1,"ph":"Reception","pd":0}',
    '*05D+~~~~4~9|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":127,"hs":0,"vs":0,"hsp":1,"vsp":1,"ph":"Transition","pd":0}',
    '*16E#~~~~~~4|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":127,"hs":0,"vs":0,"hsp":1,"vsp":1,"ph":"Transition","pd":0}',
    '*16A-X5~~4~1|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":127,"hs":0,"vs":0,"hsp":1,"vsp":1,"ph":"Transition","pd":0}',

    '*05S+~~~~1~6|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":128,"hs":1,"vs":0,"hsp":1,"vsp":1,"ph":"Serve","pd":1}',
    'a16R+~~~~5~7|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":128,"hs":1,"vs":0,"hsp":1,"vsp":1,"ph":"Reception","pd":1}',
    'a05E#K7~~~~9|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":128,"hs":1,"vs":0,"hsp":1,"vsp":1,"ph":"Reception","pd":1}',
    'a16A+V5~~4~1|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":128,"hs":1,"vs":0,"hsp":1,"vsp":1,"ph":"Reception","pd":1}',
    '*16B+~~~~~~4|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":128,"hs":1,"vs":0,"hsp":1,"vsp":1,"ph":"Reception","pd":1}',
    '*02D+~~~~2~8|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":128,"hs":1,"vs":0,"hsp":1,"vsp":1,"ph":"Transition","pd":1}',
    '*05E#K7~~~~9|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":128,"hs":1,"vs":0,"hsp":1,"vsp":1,"ph":"Transition","pd":1}',
    '*16A+V5~~4~1|{"m":"05b080cd351318b4db44bac87b101af3","s":4,"p":128,"hs":1,"vs":0,"hsp":1,"vsp":1,"ph":"Transition","pd":1}',

    # ── Second match ─────────────────────────────────────────────────────
    '*09S#~~~~7~5|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":104,"hs":4,"vs":8,"hsp":2,"vsp":4,"ph":"Serve","pd":-4}',
    'a04R+~~~~5~5|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":104,"hs":4,"vs":8,"hsp":2,"vsp":4,"ph":"Reception","pd":-4}',
    'a05E#K7~~~~8|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":104,"hs":4,"vs":8,"hsp":2,"vsp":4,"ph":"Reception","pd":-4}',
    'a06A+X8~~9~9|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":104,"hs":4,"vs":8,"hsp":2,"vsp":4,"ph":"Reception","pd":-4}',
    '*09S+~~~~5~5|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":105,"hs":5,"vs":8,"hsp":2,"vsp":4,"ph":"Serve","pd":-3}',
    '*09S=~~~~7~3|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":106,"hs":6,"vs":8,"hsp":2,"vsp":4,"ph":"Serve","pd":-2}',

    'a12R-~~~~6~6|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":107,"hs":6,"vs":9,"hsp":2,"vsp":3,"ph":"Reception","pd":-3}',
    'a05E#K7~~~~8|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":107,"hs":6,"vs":9,"hsp":2,"vsp":3,"ph":"Reception","pd":-3}',
    'a06A+X8~~9~9|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":107,"hs":6,"vs":9,"hsp":2,"vsp":3,"ph":"Reception","pd":-3}',
    '*17F+~~~~9~3|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":107,"hs":6,"vs":9,"hsp":2,"vsp":3,"ph":"Transition","pd":-3}',
    '*05E#K1~~~~3|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":107,"hs":6,"vs":9,"hsp":2,"vsp":3,"ph":"Transition","pd":-3}',
    '*05A-PP~~3~8|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":107,"hs":6,"vs":9,"hsp":2,"vsp":3,"ph":"Transition","pd":-3}',

    '*05S+~~~~1~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":108,"hs":7,"vs":9,"hsp":1,"vsp":3,"ph":"Serve","pd":-2}',
    'a12R+~~~~5~6|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":109,"hs":7,"vs":10,"hsp":1,"vsp":2,"ph":"Reception","pd":-3}',
    'a05E#K1~~~~3|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":109,"hs":7,"vs":10,"hsp":1,"vsp":2,"ph":"Reception","pd":-3}',
    'a06A#X4~~2~4|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":109,"hs":7,"vs":10,"hsp":1,"vsp":2,"ph":"Reception","pd":-3}',
    '*04S+~~~~7~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":110,"hs":8,"vs":10,"hsp":6,"vsp":2,"ph":"Serve","pd":-2}',

    'a09R+~~~~5~8|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":112,"hs":9,"vs":11,"hsp":6,"vsp":1,"ph":"Reception","pd":-2}',
    'a05E#KS~~~~2|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":112,"hs":9,"vs":11,"hsp":6,"vsp":1,"ph":"Reception","pd":-2}',
    'a15A-CB~~2~8|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":112,"hs":9,"vs":11,"hsp":6,"vsp":1,"ph":"Reception","pd":-2}',
    '*17S+~~~~7~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":113,"hs":10,"vs":11,"hsp":5,"vsp":1,"ph":"Serve","pd":-1}',

    'a16R-~~~~1~5|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":114,"hs":10,"vs":12,"hsp":5,"vsp":6,"ph":"Reception","pd":-2}',
    'a05E#K7~~~~8|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":114,"hs":10,"vs":12,"hsp":5,"vsp":6,"ph":"Reception","pd":-2}',
    'a06A-X4~~2~5|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":114,"hs":10,"vs":12,"hsp":5,"vsp":6,"ph":"Reception","pd":-2}',
    '*16B#~~~~~~4|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":114,"hs":10,"vs":12,"hsp":5,"vsp":6,"ph":"Transition","pd":-2}',
    '*06S-~~~~1~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":115,"hs":11,"vs":12,"hsp":4,"vsp":6,"ph":"Serve","pd":-1}',

    'a16R+~~~~5~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":116,"hs":11,"vs":13,"hsp":4,"vsp":5,"ph":"Reception","pd":-2}',
    'a05E#KS~~~~3|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":116,"hs":11,"vs":13,"hsp":4,"vsp":5,"ph":"Reception","pd":-2}',
    'a05A+PP~~3~4|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":116,"hs":11,"vs":13,"hsp":4,"vsp":5,"ph":"Reception","pd":-2}',
    '*06F+~~~~6~9|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":116,"hs":11,"vs":13,"hsp":4,"vsp":5,"ph":"Transition","pd":-2}',
    '*05E#KS~~~~2|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":116,"hs":11,"vs":13,"hsp":4,"vsp":5,"ph":"Transition","pd":-2}',
    '*16A#V5~~4~1|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":116,"hs":11,"vs":13,"hsp":4,"vsp":5,"ph":"Transition","pd":-2}',

    '*12S+~~~~6~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":117,"hs":12,"vs":13,"hsp":3,"vsp":5,"ph":"Serve","pd":-1}',
    'a09R+~~~~5~8|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":118,"hs":12,"vs":14,"hsp":3,"vsp":4,"ph":"Reception","pd":-2}',
    'a05E#K2~~~~3|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":118,"hs":12,"vs":14,"hsp":3,"vsp":4,"ph":"Reception","pd":-2}',
    'a15A#X2~~2~9|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":118,"hs":12,"vs":14,"hsp":3,"vsp":4,"ph":"Reception","pd":-2}',
    '*04B=~~~~~~3|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":118,"hs":12,"vs":14,"hsp":3,"vsp":4,"ph":"Transition","pd":-2}',

    'a04R+~~~~5~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":119,"hs":12,"vs":15,"hsp":3,"vsp":4,"ph":"Reception","pd":-3}',
    'a05E#K2~~~~3|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":119,"hs":12,"vs":15,"hsp":3,"vsp":4,"ph":"Reception","pd":-3}',
    'a15A#X2~~2~9|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":119,"hs":12,"vs":15,"hsp":3,"vsp":4,"ph":"Reception","pd":-3}',
    '*09S!~~~~7~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":120,"hs":13,"vs":15,"hsp":2,"vsp":4,"ph":"Serve","pd":-2}',

    'a04A+X5~~4~1|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":120,"hs":13,"vs":15,"hsp":2,"vsp":4,"ph":"Transition","pd":-2}',
    'a06A#X8~~9~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":120,"hs":13,"vs":15,"hsp":2,"vsp":4,"ph":"Transition","pd":-2}',
    '*09S+~~~~6~7|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":121,"hs":14,"vs":15,"hsp":2,"vsp":4,"ph":"Serve","pd":-1}',

    'a12R+~~~~5~6|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":122,"hs":14,"vs":16,"hsp":2,"vsp":3,"ph":"Reception","pd":-2}',
    'a05E#K7~~~~8|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":122,"hs":14,"vs":16,"hsp":2,"vsp":3,"ph":"Reception","pd":-2}',
    'a16A#X5~~4~1|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":122,"hs":14,"vs":16,"hsp":2,"vsp":3,"ph":"Reception","pd":-2}',
    '*09S-~~~~7~5|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":122,"hs":15,"vs":15,"hsp":2,"vsp":4,"ph":"Serve","pd":0}',
    'a12R-~~~~6~6|{"m":"e44723e981facc1e424b615fb599ecc8","s":3,"p":123,"hs":15,"vs":16,"hsp":2,"vsp":3,"ph":"Reception","pd":-1}',
]
