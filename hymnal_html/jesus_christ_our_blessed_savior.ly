\version "2.22.1"

\header {
  title = "129  Jesus Christ, Our Blessed Savior"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } }\mf a'2 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } } } g'8 a'4 d'4 | f'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { g'16 e'16 } f'2 | f'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } e'2 | d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } f'4 f'4 \acciaccatura { g'16 e'16 } f'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } g'2 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'8 f'4 e'4 | \acciaccatura { e'16 c'16 } d'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } f'4 f'4 f'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'2 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 f'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d''4 c''8 b'8 a'4 | f'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'2 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 f'4 e'4 | d'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | }
    { \voiceTwo <bes f'>1\p\arpeggio | <e f a c'>1\arpeggio | <d f a>1\arpeggio | <g c'>1\arpeggio | <bes, d f>1\arpeggio | <d f a>1\arpeggio | <e f a c'>1\arpeggio | <bes d'>1\arpeggio | <g, c e>1\arpeggio | <g c' e'>1\arpeggio | <g c' e'>1\arpeggio | <g c' e'>1\arpeggio | <g c' e'>1\arpeggio | <g c' e'>1\arpeggio | <g c'>1\arpeggio | <g, c e>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <g, bes, d>1\p\arpeggio | \acciaccatura { bes,,8 } <f, g, bes, d>4\arpeggio g,8 bes,8 d8 g,8 bes,4 | \acciaccatura { a,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 e4 | \acciaccatura { d,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 bes,4 | \acciaccatura { a,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { d,8 } <f, a, bes, d>4\arpeggio a,8 bes,8 d8 a,8 bes,4 | \acciaccatura { a,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 e,4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { d,8 } <bes, d f>1\arpeggio | \acciaccatura { d,8 } <bes, d f>1\arpeggio | \acciaccatura { d,8 } <bes, d f>1\arpeggio | \acciaccatura { d,8 } <bes, d f>1\arpeggio | \acciaccatura { d,8 } <bes, d f>1\arpeggio | \acciaccatura { d,8 } <bes, d f>1\arpeggio | \acciaccatura { d,8 } <bes, d f>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
