\version "2.22.1"

\header {
  title = "239  The Church's One Foundation"
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
    { \voiceOne fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf fis'4 fis'4 g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } fis'2 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 b'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { g'16 e'16 } fis'2. | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } a'4 d''4 d''4 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } cis''2 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } g'4 a'4 fis'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } e'2. | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } fis'4 g'4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } b'2 a'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d''4. cis''8 b'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'2. | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } fis'4 fis'4 \acciaccatura { a'16 fis'16 } g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'2 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 e'4 d'4 | cis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } \acciaccatura { e'16 cis'16 } d'2. | }
    { \voiceTwo <cis e g a>1\p\arpeggio | <cis e g a>1\arpeggio | <g b>1\arpeggio | <d fis a>1\arpeggio | <a cis' e'>1\arpeggio | <a cis' e'>1\arpeggio | <a b d'>1\arpeggio | <fis g b>1\arpeggio | <fis g b d'>1\arpeggio | <b d' fis'>1\arpeggio | <b d' fis'>1\arpeggio | <a cis' e'>1\arpeggio | <g a cis'>1\arpeggio | <g b d'>1\arpeggio | <g b>1\arpeggio | <fis a>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <d, fis, a, b,>1\p\arpeggio | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 b,8 fis,8 e,4 | \acciaccatura { d,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 a,4 | \acciaccatura { a,,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 g,4 | \acciaccatura { fis,8 } <fis, a, cis>4\arpeggio a,8 cis8 a,8 cis8 b,4 | \acciaccatura { a,,8 } <a, cis e g>4\arpeggio cis8 e8 g8 cis8 b,4 | \acciaccatura { a,,8 } <g, a, cis e>4\arpeggio a,8 cis8 e8 a,8 b,4 | \acciaccatura { a,,8 } <g, a, cis e>4\arpeggio a,8 cis8 e8 a,8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 cis4 | \acciaccatura { b,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 fis,4 | \acciaccatura { e,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 b,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 fis8 cis8 a,4 | \acciaccatura { d,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 a,4 | \acciaccatura { g,,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <g, b, d e>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
