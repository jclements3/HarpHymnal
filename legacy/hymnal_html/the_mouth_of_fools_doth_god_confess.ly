\version "2.22.1"

\header {
  title = "253  The Mouth of Fools Doth God Confess"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf g'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 a'4 b'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } a'4 b'4 c''4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { a'16 fis'16 } g'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 a'4 b'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 b'4 c''4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { a'16 fis'16 } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } e'4 fis'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'4 d'4 \acciaccatura { ees'16 b16 } cis'4 | d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 b'4 c''4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 b'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 c''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'4 a'8 g'8 a'4 | \acciaccatura { a'16 fis'16 } g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <b d' fis'>1\p\arpeggio | <c' e'>1\arpeggio | <b d' fis'>1\arpeggio | <b c' e'>1\arpeggio | <c' d' fis'>1\arpeggio | <b d' fis'>1\arpeggio | <c' e'>1\arpeggio | <c' e'>1\arpeggio | <c' e'>1\arpeggio | <g b d'>1\arpeggio | <g b d'>1\arpeggio | <g b>1\arpeggio | <e g b>1\arpeggio | <g b d'>1\arpeggio | <a c' e'>1\arpeggio | <a c' e'>1\arpeggio | <fis' c''>1\arpeggio | <c' e'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <g, b, d>1\p\arpeggio | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 d4 | \acciaccatura { c,8 } <c e g a>4\arpeggio e8 g8 a8 e8 d4 | \acciaccatura { c,8 } <c d fis a>4\arpeggio d8 fis8 a8 d8 e4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 b8 fis8 d4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 c4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 d4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <e g b>4\arpeggio g8 b8 g8 b8 e4 | \acciaccatura { e,8 } <e g b>4\arpeggio g8 b8 g8 b8 a4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 d4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 fis4 | \acciaccatura { e,8 } <e g b>4\arpeggio g8 b8 g8 b8 a4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 b,4 | \acciaccatura { a,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 e8 b,8 a,4 | \acciaccatura { g,,8 } <g, b, d>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
