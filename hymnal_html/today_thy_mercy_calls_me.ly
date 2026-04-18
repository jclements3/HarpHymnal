\version "2.22.1"

\header {
  title = "272  Today Thy Mercy Calls Me"
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
    { \voiceOne e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf a'4 gis'4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } cis''2 \acciaccatura { b'16 gis'16 } a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 d''4 cis''4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { b'16 gis'16 } a'2. | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'4 gis'4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } cis''2 \acciaccatura { b'16 gis'16 } a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 d''4 cis''4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { b'16 gis'16 } a'2. | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 gis'4 a'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } gis'2 e'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } fis'4 gis'4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { d''16 b'16 } cis''2. | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } a'4 gis'4 fis'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } b'2 b'4 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 b'4 a'4 | gis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } \acciaccatura { b'16 gis'16 } a'2. | }
    { \voiceTwo <gis b d'>1\p\arpeggio | <gis b d' e'>1\arpeggio | d'1 | <gis b d' e'>1\arpeggio | <gis b d'>1\arpeggio | <gis b d' e'>1\arpeggio | d'1 | <a cis' e'>1\arpeggio | <a cis' e'>1\arpeggio | <a cis'>1\arpeggio | <a cis'>1\arpeggio | <gis a cis' e'>1\arpeggio | <gis a cis'>1\arpeggio | <gis a cis'>1\arpeggio | <d' fis'>1\arpeggio | <cis' e'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { a,,8 } <a, cis e fis>1\p\arpeggio | \acciaccatura { a,,8 } <a, cis e fis>4\arpeggio cis8 e8 fis8 cis8 a,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis e fis>4\arpeggio cis8 e8 fis8 cis8 a,4 | \acciaccatura { a,,8 } <a, cis e fis>4\arpeggio cis8 e8 fis8 cis8 b,4 | \acciaccatura { a,,8 } <a, cis e fis>4\arpeggio cis8 e8 fis8 cis8 a,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 b,4 | \acciaccatura { a,,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 e4 | \acciaccatura { a,,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 fis4 | \acciaccatura { e,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 fis4 | \acciaccatura { e,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 b,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 fis8 cis8 a,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 fis8 cis8 b,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 fis8 cis8 e4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 b,4 | \acciaccatura { a,,8 } <d fis a b>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
