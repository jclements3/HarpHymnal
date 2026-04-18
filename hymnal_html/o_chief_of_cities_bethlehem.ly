\version "2.22.1"

\header {
  title = "179  O Chief of Cities Bethlehem"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf d'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } } } \acciaccatura { g'16 e'16 } fis'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } } } fis'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } \acciaccatura { e'16 cis'16 } d'2 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } a'4 b'4 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { e''16 cis''16 } d''2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } d''2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } cis''2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { cis''16 a'16 } b'2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'2 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { fis'16 d'16 } e'2 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d'2 | cis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } \acciaccatura { e'16 cis'16 } d'2 | }
    { \voiceTwo <d fis a>2.\p\arpeggio | <g a cis'>2.\arpeggio | <g a cis' e'>2.\arpeggio | <a cis'>2.\arpeggio | <g b>2.\arpeggio | <cis' d' fis'>2.\arpeggio | <cis' d' fis' a'>2.\arpeggio | <fis' g' b'>2.\arpeggio | <d' fis'>2.\arpeggio | <d' fis' a'>2.\arpeggio | <cis' d' fis'>2.\arpeggio | <g b d'>2.\arpeggio | <e g b>2.\arpeggio | <cis e g a>2.\arpeggio | <cis e g a>2.\arpeggio | <fis a>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <a, cis e>2.\p\arpeggio | \acciaccatura { a,,8 } <a, b, d fis>4\arpeggio b,8 d8 a,4 | \acciaccatura { b,,8 } <a, b, d fis>4\arpeggio b,8 d8 b,4 | \acciaccatura { a,,8 } <g, b, d>4\arpeggio b,8 d8 g,4 | \acciaccatura { g,,8 } <d, fis, a,>4\arpeggio fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, fis, g, b,>4\arpeggio fis,8 g,8 e,4 | \acciaccatura { d,8 } <d, fis, g, b,>4\arpeggio fis,8 g,8 d,4 | \acciaccatura { g,,8 } <g, a, cis e>4\arpeggio a,8 cis8 b,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 e,4 | \acciaccatura { d,8 } <d, fis, g, b,>4\arpeggio fis,8 g,8 d,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 fis,4 | \acciaccatura { e,8 } <d, fis, a,>4\arpeggio fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 d,4 | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 e,4 | \acciaccatura { d,8 } <g, b, d e>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
