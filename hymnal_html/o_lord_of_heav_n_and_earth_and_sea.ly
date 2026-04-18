\version "2.22.1"

\header {
  title = "190  O Lord of Heav'n and Earth and Sea"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } }\mf d''4 cis''8 b'8 a'4 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'8 g'8 fis'8 e'4 d'4 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } g'8 a'4 a'4 \acciaccatura { cis''16 a'16 } b'4 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } d''4 d''8 e''8 cis''4 | d''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } cis''8 b'4 a'4 \acciaccatura { a'16 fis'16 } g'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } } } fis'4. g'8 a'4 | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } e'8 fis'2 e'2 | \acciaccatura { e'16 cis'16 } d'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } | }
    { \voiceTwo <cis' d' fis'>1\p\arpeggio | <g b>1\arpeggio | <cis' d'>1\arpeggio | <cis' d' fis' a'>1\arpeggio | <d' fis'>1\arpeggio | <g a cis'>1\arpeggio | <d fis a>1\arpeggio | <cis e g a>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <d, fis, g, b,>1\p\arpeggio | \acciaccatura { g,,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, e, g, b,>4\arpeggio e,8 g,8 b,8 e,8 d,4 | \acciaccatura { e,8 } <d, e, g, b,>4\arpeggio e,8 g,8 b,8 e,8 e,4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 a,4 | \acciaccatura { a,,8 } <a, b, d fis>4\arpeggio b,8 d8 fis8 b,8 cis4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <d, fis, a, b,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
