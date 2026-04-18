\version "2.22.1"

\header {
  title = "139  Joy to the World"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \major
  \time 2/4
}

upper = {
  \global
  <<
    { \voiceOne d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf cis''8. b'16 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } e'4 | d'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } a'8 | b'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } b'8 | cis''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } cis''8 | d''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''8 | d''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } cis''8 b'8 a'8 | a'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'16 fis'8 d''8 | d''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } cis''8 b'8 a'8 | a'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'16 fis'8 fis'8 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } fis'8 fis'8 fis'16 g'16 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } g'16 fis'16 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } e'8 e'8 e'16 fis'16 | g'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } fis'16 e'16 | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 b'8 | a'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'16 fis'8 g'8 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } e'4 | \acciaccatura { e'16 cis'16 } d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo g'2\p | <g b d'>2\arpeggio | <cis e g a>2\arpeggio | <cis' fis'>2\arpeggio | <a cis' e'>2\arpeggio | <d' fis' a'>2\arpeggio | <d' fis' a'>2\arpeggio | <d' fis'>2\arpeggio | d'2 | <d' fis'>2\arpeggio | d'2 | <d fis a>2\arpeggio | <a b d'>2\arpeggio | <g a cis'>2\arpeggio | <g a cis'>2\arpeggio | g'2 | <cis' e'>2\arpeggio | <cis e g a>2\arpeggio | <g b>2\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <d, fis, a,>2\p\arpeggio | \acciaccatura { d,8 } <d, fis, a,>2\arpeggio | \acciaccatura { d,8 } <d, fis, a, b,>2\arpeggio | \acciaccatura { d,8 } <d, fis, g, b,>2\arpeggio | \acciaccatura { g,,8 } <g, b, d>2\arpeggio | \acciaccatura { a,,8 } <a, cis e>2\arpeggio | \acciaccatura { d,8 } <a, cis e>2\arpeggio | \acciaccatura { d,8 } <a, cis e>2\arpeggio | \acciaccatura { d,8 } <a, cis e>2\arpeggio | \acciaccatura { d,8 } <a, cis e>2\arpeggio | \acciaccatura { d,8 } <a, cis e>2\arpeggio | \acciaccatura { d,8 } <a, cis e>2\arpeggio | \acciaccatura { a,,8 } <a, cis e g>2\arpeggio | \acciaccatura { a,,8 } <a, cis d fis>2\arpeggio | \acciaccatura { a,,8 } <a, cis d fis>2\arpeggio | \acciaccatura { d,8 } <d, fis, a,>2\arpeggio | \acciaccatura { d,8 } <d, fis, a, b,>2\arpeggio | \acciaccatura { d,8 } <d, fis, a, b,>2\arpeggio | \acciaccatura { d,8 } <d, fis, a,>2\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
