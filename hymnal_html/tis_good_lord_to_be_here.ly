\version "2.22.1"

\header {
  title = "267  Tis Good, Lord, To Be Here"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key e \major
  \time 2/4
}

upper = {
  \global
  <<
    { \voiceOne e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf fis'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } \acciaccatura { a'16 fis'16 } gis'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { dis''16 b'16 } cis''4 | e''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } dis''4 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 | gis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { b'16 gis'16 } a'4 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } \acciaccatura { a'16 fis'16 } gis'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } \acciaccatura { gis'16 e'16 } fis'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } gis'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { fis'16 dis'16 } e'4 | }
    { \voiceTwo <a cis'>2\p\arpeggio | <b dis' fis'>2\arpeggio | <gis cis'>2\arpeggio | <cis' e' gis'>2\arpeggio | <cis' e' gis'>2\arpeggio | <fis' a'>2\arpeggio | <dis e gis b>2\arpeggio | <b dis' fis'>2\arpeggio | <b dis' fis'>2\arpeggio | <fis a cis'>2\arpeggio | <dis e gis b>2\arpeggio | <b dis' fis'>2\arpeggio | <gis cis'>2\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { e,8 } <e, gis, b,>2\p\arpeggio | \acciaccatura { a,,8 } <a, cis e>2\arpeggio | \acciaccatura { b,,8 } <b, dis fis>2\arpeggio | \acciaccatura { b,,8 } <b, dis fis>2\arpeggio | \acciaccatura { cis,8 } <fis, a, cis>2\arpeggio | \acciaccatura { fis,8 } <e, gis, b,>2\arpeggio | \acciaccatura { e,8 } <e, gis, a, cis>2\arpeggio | \acciaccatura { a,,8 } <a, cis e>2\arpeggio | \acciaccatura { b,,8 } <fis, a, cis>2\arpeggio | \acciaccatura { fis,8 } <e, gis, b,>2\arpeggio | \acciaccatura { e,8 } <e, fis, a, cis>2\arpeggio | \acciaccatura { fis,8 } <fis, a, cis>2\arpeggio | \acciaccatura { b,,8 } <b, dis fis>2\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
