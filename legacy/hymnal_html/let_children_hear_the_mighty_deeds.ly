\version "2.22.1"

\header {
  title = "143  Let Children Hear The Mighty Deeds"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key a \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf cis''4 a'4 fis'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 b'4 cis''4 | e''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } cis''4 a'4 \acciaccatura { gis'16 e'16 } fis'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'2. | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } cis''8 d''4 d''4 cis''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } fis'4 b'4 \acciaccatura { a'16 fis'16 } gis'4 | e''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''8 cis''4 cis''4 b'4 | gis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } \acciaccatura { b'16 gis'16 } a'2. | }
    { \voiceTwo <gis b d'>1\p\arpeggio | <a cis'>1\arpeggio | r1 | <a cis'>1\arpeggio | <a cis' e'>1\arpeggio | <a cis' e'>1\arpeggio | a'1 | <cis' e'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { a,,8 } <a, cis e fis>1\p\arpeggio | \acciaccatura { a,,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 fis4 | \acciaccatura { e,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 e4 | \acciaccatura { e,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 fis4 | \acciaccatura { e,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 b,4 | \acciaccatura { a,,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 e4 | \acciaccatura { e,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 b,4 | \acciaccatura { a,,8 } <d fis a b>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
