\version "2.22.1"

\header {
  title = "199  O Trinity of Blessed Light"
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
    { \voiceOne a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "ø7" \raise #0.6 \smaller "2" } } }\mf b'8 a'8 g'8 fis'8 g'8 e'8 fis'8 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'8 b'8 b'8 a'8 a'4 a'8 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'8 g'8 fis'8 g'8 e'8 fis'8 g'8 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } b'8 b'8 a'8 a'4 a'8 b'8 | d''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } cis''8 d''8 b'8 a'8 g'8 a'8 b'8 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } g'8 fis'8 fis'4 g'8 a'8 a'8 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } fis'8 g'8 e'8 fis'8 g'8 a'8 b'8 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "Iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "°" } } } a'8 \acciaccatura { b'16 gis'16 } a'4 | }
    { \voiceTwo <cis' d'>1\p\arpeggio | <gis b d'>1\arpeggio | <b d'>1\arpeggio | <gis a cis' e'>1\arpeggio | gis'1 | <gis b d'>1\arpeggio | <gis b d'>1\arpeggio | <e a cis'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <d fis gis b>1\p\arpeggio | \acciaccatura { gis,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 cis4 | \acciaccatura { b,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 fis8 cis8 a,4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 a4 | \acciaccatura { gis,8 } <gis b d'>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
