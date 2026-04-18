\version "2.22.1"

\header {
  title = "266  Through the Night of Doubt and Sorrow"
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
    { \voiceOne a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf e'4 a'4 b'4 | cis''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d''8 cis''4 b'4 | e''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'4 b'4 cis''8 d''8 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'4 \acciaccatura { d''16 b'16 } cis''2 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } b'4 cis''4 e''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } gis'4 gis'4 fis'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 e''4 gis'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } fis'4 e'2 | e'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } fis'8 gis'4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } gis'4 fis'4 e'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 cis''8 d''8 e''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } cis''4 b'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'4 a'4 \acciaccatura { cis''16 a'16 } b'4 | cis''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d''8 cis''4 b'4 | e''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'4 d''4 cis''4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'4 \acciaccatura { b'16 gis'16 } a'2 | }
    { \voiceTwo <d' fis'>1\p\arpeggio | <gis b d' e'>1\arpeggio | gis'1 | <gis b d' e'>1\arpeggio | a'1 | <gis b d'>1\arpeggio | d''1 | <e gis b>1\arpeggio | r1 | <fis a cis'>1\arpeggio | fis'1 | <d' e' gis'>1\arpeggio | <d' fis'>1\arpeggio | <gis b d' e'>1\arpeggio | <gis' b'>1\arpeggio | <gis b d' e'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { a,,8 } <a, cis e>1\p\arpeggio | \acciaccatura { a,,8 } <a, cis e fis>4\arpeggio cis8 e8 fis8 cis8 b,4 | \acciaccatura { a,,8 } <a, cis e fis>4\arpeggio cis8 e8 fis8 cis8 b,4 | \acciaccatura { a,,8 } <a, cis e fis>4\arpeggio cis8 e8 fis8 cis8 a,4 | \acciaccatura { a,,8 } <fis a cis'>4\arpeggio a8 cis'8 a8 cis'8 gis4 | \acciaccatura { fis,8 } <fis a cis'>4\arpeggio a8 cis'8 a8 cis'8 a4 | \acciaccatura { gis,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 fis4 | \acciaccatura { e,8 } <cis e gis>4\arpeggio e8 gis8 e8 gis8 fis4 | \acciaccatura { e,8 } <cis e gis>4\arpeggio e8 gis8 e8 gis8 d4 | \acciaccatura { cis,8 } <cis e gis>4\arpeggio e8 gis8 e8 gis8 gis4 | \acciaccatura { fis,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 fis4 | \acciaccatura { e,8 } <e gis a cis'>4\arpeggio gis8 a8 cis'8 gis8 b,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 a,4 | \acciaccatura { a,,8 } <a, cis e fis>4\arpeggio cis8 e8 fis8 cis8 b,4 | \acciaccatura { a,,8 } <a, cis e fis>4\arpeggio cis8 e8 fis8 cis8 b,4 | \acciaccatura { a,,8 } <a, cis e fis>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
