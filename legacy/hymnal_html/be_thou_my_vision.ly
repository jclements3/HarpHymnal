\version "2.22.1"

\header {
  title = "036  Be Thou My Vision"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \minor
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf ees'4 f'8 ees'8 | c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } bes4 bes8 c'8 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ees'4 f'4 | g'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } f'4 f'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } g'4 \acciaccatura { c''16 a'16 } bes'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } bes'4 g'4 | bes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "ø7" \raise #0.6 \smaller "2" } } } | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "°" } } } c''8 d''8 ees''8 d''8 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 g'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } ees'4 d'4 | c'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 bes'4 | c''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "°" } } } bes'8 g'4 ees'8 g'8 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } ees'4 ees'4 | \acciaccatura { f'16 d'16 } ees'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } | }
    { \voiceTwo <f a c' d'>2.\p\arpeggio | <f, a, c d>2.\arpeggio | <c ees g>2.\arpeggio | <c' ees'>2.\arpeggio | <f g bes d'>2.\arpeggio | <f g bes d'>2.\arpeggio | <f g bes d'>2.\arpeggio | <bes c' ees' g'>2.\arpeggio | <g' bes'>2.\arpeggio | <c' ees'>2.\arpeggio | g'2. | <f a>2.\arpeggio | <f a c'>2.\arpeggio | <g bes d'>2.\arpeggio | <f g bes d'>2.\arpeggio | <f a c'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { bes,,8 } <g, bes, d ees>2.\p\arpeggio | \acciaccatura { bes,,8 } <g, bes, d ees>4\arpeggio bes,8 d8 c4 | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 f4 | \acciaccatura { ees,8 } <g, bes, d>4\arpeggio bes,8 d8 c4 | \acciaccatura { bes,,8 } <g, bes, c ees>4\arpeggio bes,8 c8 c4 | \acciaccatura { bes,,8 } <g, bes, c ees>4\arpeggio bes,8 c8 g,4 | \acciaccatura { bes,,8 } <g, bes, c ees>4\arpeggio bes,8 c8 f4 | \acciaccatura { ees,8 } <c ees f a>4\arpeggio ees8 f8 bes,4 | \acciaccatura { a,,8 } <f a c'>4\arpeggio a8 c'8 c4 | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 f4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 a,4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 bes,4 | \acciaccatura { a,,8 } <f a c'>4\arpeggio a8 c'8 c4 | \acciaccatura { bes,,8 } <g, bes, c ees>4\arpeggio bes,8 c8 f4 | \acciaccatura { ees,8 } <c ees g>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
