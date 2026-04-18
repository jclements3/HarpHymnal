\version "2.22.1"

\header {
  title = "171  None Other Lamb"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key fis \minor
  \time 3/2
}

upper = {
  \global
  <<
    { \voiceOne a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf g'4 g'4 | fis'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 g'4 | fis'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 a'4 | d''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } cis''8 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 gis'4 | a'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 a'4 | b'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'8 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 g'4 | fis'1.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "2" } } } | r1. | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } fis'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | \acciaccatura { gis'16 e'16 } fis'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "Vii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } | }
    { \voiceTwo <b d' fis'>1.\p\arpeggio | <b d'>1.\arpeggio | <b d' fis'>1.\arpeggio | <b d'>1.\arpeggio | <gis b d'>1.\arpeggio | gis'1. | <b d'>1.\arpeggio | <gis b d'>1.\arpeggio | <gis b d'>1.\arpeggio | <d' fis'>1.\arpeggio | <d' fis'>1.\arpeggio | <fis gis b d'>1.\arpeggio | <fis' gis' b' d''>1.\arpeggio | <fis a cis'>1.\arpeggio | <b d' fis'>1.\arpeggio | <gis cis' e'>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { a,,8 } <fis, a, cis>1.\p\arpeggio | \acciaccatura { d,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 b,4 | \acciaccatura { a,,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 e4 | \acciaccatura { d,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 b,4 | \acciaccatura { a,,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 cis4 | \acciaccatura { b,,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 b,4 | \acciaccatura { a,,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 b,4 | \acciaccatura { a,,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 b,4 | \acciaccatura { a,,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 cis4 | \acciaccatura { b,,8 } <gis, b, d>4\arpeggio b,8 d8 b,8 d8 b,8 d8 b,8 d8 gis,4 | \acciaccatura { fis,8 } <gis, b, d>4\arpeggio b,8 d8 b,8 d8 b,8 d8 b,8 d8 cis4 | \acciaccatura { b,,8 } <gis, b, cis e>4\arpeggio b,8 cis8 e8 b,8 cis8 e8 b,8 cis8 cis4 | \acciaccatura { b,,8 } <gis, b, cis e>4\arpeggio b,8 cis8 e8 b,8 cis8 e8 b,8 cis8 fis4 | \acciaccatura { e,8 } <cis e gis>4\arpeggio e8 gis8 e8 gis8 e8 gis8 e8 gis8 b,4 | \acciaccatura { a,,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 e4 | \acciaccatura { d,8 } <b, d fis>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
