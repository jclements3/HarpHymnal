\version "2.22.1"

\header {
  title = "055  Come, God Creator, Holy Ghost"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key c \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } }\mf a'4 g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } g'4 c''4 d''4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { d''16 b'16 } c''4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } a'4 c''4 d''4 | e''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e''4 \acciaccatura { e''16 c''16 } d''2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } e''4 c''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "2" } } } g'4 b'4 c''4 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } \acciaccatura { a'16 f'16 } g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'4 f'4 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 g'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { a'16 f'16 } g'2 | }
    { \voiceTwo <b c' e'>1\p\arpeggio | <b c' e'>1\arpeggio | <b c' e' g'>1\arpeggio | <b c' e'>1\arpeggio | <e' g' b'>1\arpeggio | <e' g' b'>1\arpeggio | <c' d' f'>1\arpeggio | b'1 | <a c' e'>1\arpeggio | <c' e'>1\arpeggio | <b d' f'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <c, e, f, a,>1\p\arpeggio | \acciaccatura { c,8 } <c, e, f, a,>4\arpeggio e,8 f,8 a,8 e,8 d,4 | \acciaccatura { c,8 } <c, e, f, a,>4\arpeggio e,8 f,8 a,8 e,8 c,4 | \acciaccatura { f,8 } <c, e, f, a,>4\arpeggio e,8 f,8 a,8 e,8 d,4 | \acciaccatura { c,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 c,4 | \acciaccatura { e,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 e,4 | \acciaccatura { d,8 } <d, f, g, b,>4\arpeggio f,8 g,8 b,8 f,8 a,4 | \acciaccatura { g,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 f,4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 b,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 c8 e8 d4 | \acciaccatura { c,8 } <c, e, g, a,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
