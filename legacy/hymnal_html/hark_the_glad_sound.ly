\version "2.22.1"

\header {
  title = "087  Hark the Glad Sound"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf g'4 b'4 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 a'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { c''16 a'16 } b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } } } d''4 g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 e'4 | d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 \acciaccatura { a'16 fis'16 } g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } b'4 a'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } c''4 b'4 | e''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 fis'4 | \acciaccatura { a'16 fis'16 } g'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <g b>2.\p\arpeggio | <e' g' b'>2.\arpeggio | <g b d'>2.\arpeggio | <g b d'>2.\arpeggio | <c' d' fis'>2.\arpeggio | <e g b>2.\arpeggio | <g b>2.\arpeggio | <g b d'>2.\arpeggio | <c' d' fis'>2.\arpeggio | <fis' g'>2.\arpeggio | <c' e'>2.\arpeggio | <c' g'>2.\arpeggio | <c' e'>2.\arpeggio | <c' e'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <d fis a>2.\p\arpeggio | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis4 | \acciaccatura { e,8 } <e g b>4\arpeggio g8 b8 a4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 d4 | \acciaccatura { d,8 } <d e g b>4\arpeggio e8 g8 fis4 | \acciaccatura { e,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 d4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 a,4 | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 d4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 d4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 d4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
