\version "2.22.1"

\header {
  title = "180  O Come O Come Emmanuel"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key e \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf g'4 b'4 b'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'4 c''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'2. | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'4 g'4 e'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 fis'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "2" } } } \acciaccatura { fis'16 d'16 } e'2. | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 e'4 e'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'2 fis'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d'2. | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 b'4 \acciaccatura { c''16 a'16 } b'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'4 c''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'2. | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''2. | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } \acciaccatura { c''16 a'16 } b'2. | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 c''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { a'16 fis'16 } g'2. | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'4 g'4 e'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 fis'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { fis'16 d'16 } e'2. | }
    { \voiceTwo r1 | <d' fis'>1\arpeggio | <d fis a b>1\arpeggio | <d' fis'>1\arpeggio | <e g b>1\arpeggio | <b, c e g>1\arpeggio | <b d' fis'>1\arpeggio | <b d'>1\arpeggio | <c e g>1\arpeggio | e'1 | <d' fis'>1\arpeggio | <g b d'>1\arpeggio | <g' b'>1\arpeggio | <g a c' e'>1\arpeggio | <e' g'>1\arpeggio | <e g b>1\arpeggio | <d' fis'>1\arpeggio | <e g b>1\arpeggio | <e g b>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { e,8 } <c e g>1\p\arpeggio | \acciaccatura { g,,8 } <e, g, b, c>4\arpeggio g,8 b,8 c8 g,8 a,4 | \acciaccatura { g,,8 } <e, g, b, c>4\arpeggio g,8 b,8 c8 g,8 a,4 | \acciaccatura { g,,8 } <e, g, b, c>4\arpeggio g,8 b,8 c8 g,8 a,4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 e8 g8 fis4 | \acciaccatura { e,8 } <c e fis a>4\arpeggio e8 fis8 a8 e8 c4 | \acciaccatura { a,,8 } <fis, a, c>4\arpeggio a,8 c8 a,8 c8 e4 | \acciaccatura { d,8 } <fis, a, c>4\arpeggio a,8 c8 a,8 c8 b,4 | \acciaccatura { a,,8 } <fis, a, c>4\arpeggio a,8 c8 a,8 c8 fis,4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { g,,8 } <e, g, b, c>4\arpeggio g,8 b,8 c8 g,8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 c4 | \acciaccatura { b,,8 } <g, b, d fis>4\arpeggio b,8 d8 fis8 b,8 g,4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 e8 g8 fis4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { g,,8 } <e, g, b, c>4\arpeggio g,8 b,8 c8 g,8 a,4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 e8 g8 fis4 | \acciaccatura { e,8 } <c e g>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
