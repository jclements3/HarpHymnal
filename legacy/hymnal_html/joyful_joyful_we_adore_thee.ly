\version "2.22.1"

\header {
  title = "140  Joyful, Joyful, We Adore Thee"
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
    { \voiceOne b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf b'4 c''4 d''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 b'4 \acciaccatura { b'16 g'16 } a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 a'4 b'4 | b'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'8 \acciaccatura { b'16 g'16 } a'2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 c''4 d''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } c''4 b'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 a'4 b'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } g'8 \acciaccatura { a'16 fis'16 } g'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } a'4 b'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'8 c''8 b'4 \acciaccatura { a'16 fis'16 } g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } b'8 c''8 b'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 d'2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } b'4 c''4 \acciaccatura { e''16 c''16 } d''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } c''4 b'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 a'4 b'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } g'8 \acciaccatura { a'16 fis'16 } g'2 | }
    { \voiceTwo g'1\p | g'1 | <c' e'>1\arpeggio | <fis a c' d'>1\arpeggio | <a c' e'>1\arpeggio | <fis' g'>1\arpeggio | <g b d'>1\arpeggio | <d e g b>1\arpeggio | <c' d' fis'>1\arpeggio | <g b d'>1\arpeggio | <d' e' g'>1\arpeggio | <g b>1\arpeggio | <fis' g'>1\arpeggio | <fis' g'>1\arpeggio | <g b d'>1\arpeggio | <d e g b>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <d fis a>1\p\arpeggio | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 d4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 e8 b,8 g,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 b,4 | \acciaccatura { a,,8 } <g, a, c e>4\arpeggio a,8 c8 e8 a,8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 e4 | \acciaccatura { d,8 } <d fis a c'>4\arpeggio fis8 a8 c'8 fis8 d4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 b8 fis8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 d4 | \acciaccatura { d,8 } <d fis a c'>4\arpeggio fis8 a8 c'8 fis8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 a,4 | \acciaccatura { g,,8 } <g, a, c e>4\arpeggio a,8 c8 e8 a,8 g,4 | \acciaccatura { a,,8 } <g, a, c e>4\arpeggio a,8 c8 e8 a,8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 e4 | \acciaccatura { d,8 } <d fis a c'>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
