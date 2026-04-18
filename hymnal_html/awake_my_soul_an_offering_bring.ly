\version "2.22.1"

\header {
  title = "030  Awake My Soul, An Offering Bring"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "+8" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf bes'4 c''4 d''4. | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "¹" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 g'4 fis'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4. c''8 d''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 a'4 bes'2 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'8 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 bes'4 \acciaccatura { bes'16 g'16 } a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4. bes'8 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 fis'4 \acciaccatura { a'16 f'16 } g'2 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'8 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 bes'4 \acciaccatura { bes'16 g'16 } a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 bes'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "+8" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 fis'4 g'2 | r1 | }
    { \voiceTwo <ees g bes ees'>1\p\arpeggio | d'1 | g'1 | <g bes d'>1\arpeggio | <g bes d'>1\arpeggio | <g bes d'>1\arpeggio | g'1 | <g bes d'>1\arpeggio | <g bes d'>1\arpeggio | <g bes d'>1\arpeggio | g'1 | <ees g bes ees'>1\arpeggio | <d'' g'' bes''>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <ees g bes>1\p\arpeggio | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <d g bes ees'>4\arpeggio g8 bes8 ees'8 g8 c4 | \acciaccatura { bes,,8 } <d g bes ees'>4\arpeggio g8 bes8 ees'8 g8 c4 | \acciaccatura { bes,,8 } <d g bes ees'>4\arpeggio g8 bes8 ees'8 g8 a,4 | \acciaccatura { g,,8 } <d g bes ees'>4\arpeggio g8 bes8 ees'8 g8 d4 | \acciaccatura { bes,,8 } <d g bes ees'>4\arpeggio g8 bes8 ees'8 g8 a,4 | \acciaccatura { g,,8 } <d g bes ees'>4\arpeggio g8 bes8 ees'8 g8 d4 | \acciaccatura { bes,,8 } <d g bes ees'>4\arpeggio g8 bes8 ees'8 g8 a,4 | \acciaccatura { g,,8 } <d g bes ees'>4\arpeggio g8 bes8 ees'8 g8 d4 | \acciaccatura { bes,,8 } <d g bes ees'>4\arpeggio g8 bes8 ees'8 g8 a,4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
