\version "2.22.1"

\header {
  title = "200  O Wondrous Type, O Vision Fair"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key cis \minor
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf cis''2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } cis''2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } b'4 \acciaccatura { b'16 gis'16 } a'2 | gis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } cis''4 b'4 | gis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } fis'4 gis'4 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } cis'8 e'4 dis'2 | \acciaccatura { dis'16 b16 } cis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } | gis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } b'2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } cis''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } gis'4 fis'2 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } gis'2 | gis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { gis'16 e'16 } fis'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } e'4 dis'2 | \acciaccatura { dis'16 b16 } cis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } | }
    { \voiceTwo <cis' e' gis'>2.\p\arpeggio | <e' gis'>2.\arpeggio | <a cis' e'>2.\arpeggio | <cis' e'>2.\arpeggio | <dis' fis' a'>2.\arpeggio | <cis' e'>2.\arpeggio | <dis e gis b>2.\arpeggio | <dis e gis b>2.\arpeggio | <cis' e'>2.\arpeggio | <b dis' fis' gis'>2.\arpeggio | <b dis'>2.\arpeggio | <cis e gis>2.\arpeggio | cis'2. | <fis b dis'>2.\arpeggio | <a cis'>2.\arpeggio | <e fis a>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { cis,8 } <a, cis e>2.\p\arpeggio | \acciaccatura { e,8 } <cis, e, gis,>4\arpeggio e,8 gis,8 a,4 | \acciaccatura { gis,,8 } <e, gis, b,>4\arpeggio gis,8 b,8 e,4 | \acciaccatura { cis,8 } <a, cis e>4\arpeggio cis8 e8 fis,4 | \acciaccatura { e,8 } <cis, e, gis,>4\arpeggio e,8 gis,8 fis,4 | \acciaccatura { e,8 } <a, cis e>4\arpeggio cis8 e8 dis4 | \acciaccatura { cis,8 } <e, gis, a, cis>4\arpeggio gis,8 a,8 a,4 | \acciaccatura { gis,,8 } <e, gis, a, cis>4\arpeggio gis,8 a,8 e,4 | \acciaccatura { cis,8 } <a, cis e>4\arpeggio cis8 e8 fis,4 | \acciaccatura { e,8 } <cis, e, gis, a,>4\arpeggio e,8 gis,8 fis,4 | \acciaccatura { e,8 } <cis, e, gis, a,>4\arpeggio e,8 gis,8 fis,4 | \acciaccatura { e,8 } <a, cis e>4\arpeggio cis8 e8 fis,4 | \acciaccatura { e,8 } <a, cis e>4\arpeggio cis8 e8 dis4 | \acciaccatura { cis,8 } <a, cis e>4\arpeggio cis8 e8 a,4 | \acciaccatura { cis,8 } <e, gis, b,>4\arpeggio gis,8 b,8 a,4 | \acciaccatura { gis,,8 } <e, gis, b, dis>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
