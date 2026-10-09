# Human labels: 40 pairs of FOMC statements

For each pair, read what changed from the previous statement to this one and decide:
is the NEW statement more **hawkish** (H: leaning towards higher rates / less support),
more **dovish** (D: leaning towards lower rates / more support), or about the **same** (S)?
All 40 are meetings where the rate did NOT change, so judge only the wording.
Try not to use what you remember about how markets reacted.

Labels go in the `label` column of `human_labels.csv` (H, D or S); `analysis.py` part M
compares every model with them. The pairs are a random draw (seed 7) of pre-2024 hold meetings.

`- removed` = text in the previous statement only; `+ added` = text in the new statement only.

## 1. 2000-12-19  (previous: 2000-11-15)

- removed: The utilization of the pool of available workers remains at an unusually high level, and the increase in energy prices, though having limited effect on core measures of prices to date, still harbors the possibility of raising inflation expectations.
- removed: The Committee, accordingly, continues to see a risk of heightened inflation pressures.
- removed: However, softening in business and household demand and tightening conditions in financial markets over recent months suggest that the economy could expand for a time at a pace below the productivity-enhanced rate of growth of its potential to produce.
- removed: Nonetheless, to date the easing of demand pressures has not been sufficient to warrant a change in the Committee's judgment that against the background of its long-run goals of price stability and sustainable economic growth and of the information currently available, the risks continue to be weighted mainly toward conditions that may generate heightened inflation pressures in the foreseeable future.
+ added: The drag on demand and profits from rising energy costs, as well as eroding consumer confidence, reports of substantial shortfalls in sales and earnings, and stress in some segments of the financial markets suggest that economic growth may be slowing further.
+ added: While some inflation risks persist, they are diminished by the more moderate pace of economic activity and by the absence of any indication that longer-term inflation expectations have increased.
+ added: The Committee will continue to monitor closely the evolving economic situation.
+ added: Against the background of its long-run goals of price stability and sustainable economic growth and of the information currently available, the Committee consequently believes that the risks are weighted mainly toward conditions that may generate economic weakness in the foreseeable future.

## 2. 2002-01-30  (previous: 2001-12-11)

- removed: The Federal Open Market Committee decided today to lower its target for the federal funds rate by 25 basis points to 1-3/4 percent.
- removed: In a related action, the Board of Governors approved a 25 basis point reduction in the discount rate to 1-1/4 percent.
- removed: Economic activity remains soft, with underlying inflation likely to edge lower from relatively modest levels.
- removed: To be sure, weakness in demand shows signs of abating, but those signs are preliminary and tentative.
- removed: The Committee continues to believe that, against the background of its long-run goals of price stability and sustainable economic growth and of the information currently available, the risks are weighted mainly toward conditions that may generate economic weakness in the foreseeable future.
- removed: Although the necessary reallocation of resources to enhance security may restrain advances in productivity for a time, the long-term prospects for productivity growth and the economy remain favorable and should become evident once the unusual forces restraining demand abate.
- removed: In taking the discount rate action, the Federal Reserve Board approved the requests submitted by the Boards of Directors of the Federal Reserve Banks of Boston, New York, Philadelphia, Chicago and San Francisco.
+ added: The Federal Open Market Committee decided today to keep its target for the federal funds rate unchanged at 1-3/4 percent.
+ added: Signs that weakness in demand is abating and economic activity is beginning to firm have become more prevalent.
+ added: With the forces restraining the economy starting to diminish, and with the long-term prospects for productivity growth remaining favorable and monetary policy accommodative, the outlook for economic recovery has become more promising.
+ added: The degree of any strength in business capital and household spending, however, is still uncertain.
+ added: Hence, the Committee continues to believe that, against the background of its long-run goals of price stability and sustainable economic growth and of the information currently available, the risks are weighted mainly toward conditions that may generate economic weakness in the foreseeable future.

## 3. 2002-03-19  (previous: 2002-01-30)

- removed: Signs that weakness in demand is abating and economic activity is beginning to firm have become more prevalent.
- removed: With the forces restraining the economy starting to diminish, and with the long-term prospects for productivity growth remaining favorable and monetary policy accommodative, the outlook for economic recovery has become more promising.
- removed: The degree of any strength in business capital and household spending, however, is still uncertain.
- removed: Hence, the Committee continues to believe that, against the background of its long-run goals of price stability and sustainable economic growth and of the information currently available, the risks are weighted mainly toward conditions that may generate economic weakness in the foreseeable future.
+ added: The information that has become available since the last meeting of the Committee indicates that the economy, bolstered by a marked swing in inventory investment, is expanding at a significant pace.
+ added: Nonetheless, the degree of the strengthening in final demand over coming quarters, an essential element in sustained economic expansion, is still uncertain.
+ added: In these circumstances, although the stance of monetary policy is currently accommodative, the Committee believes that, for the foreseeable future, against the background of its long-run goals of price stability and sustainable economic growth and of the information currently available, the risks are balanced with respect to the prospects for both goals.
+ added: The Committee decided to include in its announcements following its meetings the roll call of the vote on the federal funds rate target, including the preferred policy choice of any dissenters.
+ added: This action accelerates the release of this information, currently available in the Minutes with a lag.
+ added: To conform to this new practice, the Board of Governors also decided to report in the written announcement the roll call of any vote on the discount rate, also including the preferred policy choice of any dissenters.

## 4. 2002-05-07  (previous: 2002-03-19)

- removed: The Federal Open Market Committee decided today to keep its target for the federal funds rate unchanged at 1-3/4 percent.
- removed: The information that has become available since the last meeting of the Committee indicates that the economy, bolstered by a marked swing in inventory investment, is expanding at a significant pace.
+ added: The Federal Open Market Committee decided today to keep its target for the federal funds rate unchanged at 1 3/4 percent.
+ added: The information that has become available since the last meeting of the Committee confirms that economic activity has been receiving considerable upward impetus from a marked swing in inventory investment.
- removed: In these circumstances, although the stance of monetary policy is currently accommodative, the Committee believes that, for the foreseeable future, against the background of its long-run goals of price stability and sustainable economic growth and of the information currently available, the risks are balanced with respect to the prospects for both goals.
- removed: The Committee decided to include in its announcements following its meetings the roll call of the vote on the federal funds rate target, including the preferred policy choice of any dissenters.
- removed: This action accelerates the release of this information, currently available in the Minutes with a lag.
- removed: To conform to this new practice, the Board of Governors also decided to report in the written announcement the roll call of any vote on the discount rate, also including the preferred policy choice of any dissenters.
+ added: In these circumstances, although the stance of monetary policy is currently accommodative, the Committee believes that, for the foreseeable future, against the background of its long run goals of price stability and sustainable economic growth and of the information currently available, the risks are balanced with respect to the prospects for both goals.

## 5. 2002-06-26  (previous: 2002-05-07)

- removed: The information that has become available since the last meeting of the Committee confirms that economic activity has been receiving considerable upward impetus from a marked swing in inventory investment.
- removed: Nonetheless, the degree of the strengthening in final demand over coming quarters, an essential element in sustained economic expansion, is still uncertain.
+ added: The information that has become available since the last meeting of the Committee confirms that economic activity is continuing to increase.
+ added: However, both the upward impetus from the swing in inventory investment and the growth in final demand appear to have moderated.
+ added: The Committee expects the rate of increase of final demand to pick up over coming quarters, supported in part by robust underlying growth in productivity, but the degree of the strengthening remains uncertain.

## 6. 2002-12-10  (previous: 2002-11-06)

- removed: The Federal Open Market Committee decided today to lower its target for the federal funds rate by 50 basis points to 1 1/4 percent.
- removed: In a related action, the Board of Governors approved a 50 basis point reduction in the discount rate to 3/4 percent.
- removed: The Committee continues to believe that an accommodative stance of monetary policy, coupled with still-robust underlying growth in productivity, is providing important ongoing support to economic activity.
- removed: However, incoming economic data have tended to confirm that greater uncertainty, in part attributable to heightened geopolitical risks, is currently inhibiting spending, production, and employment.
- removed: Inflation and inflation expectations remain well contained.
- removed: In these circumstances, the Committee believes that today's additional monetary easing should prove helpful as the economy works its way through this current soft spot.
- removed: With this action, the Committee believes that, against the background of its long-run goals of price stability and sustainable economic growth and of the information currently available, the risks are balanced with respect to the prospects for both goals in the foreseeable future.
+ added: The Federal Open Market Committee decided today to keep its target for the federal funds rate unchanged at 1-1/4 percent.
+ added: The Committee continues to believe that this accommodative stance of monetary policy, coupled with still robust underlying growth in productivity, is providing important ongoing support to economic activity.
+ added: The limited number of incoming economic indicators since the November meeting, taken together, are not inconsistent with the economy working its way through its current soft spot.
+ added: In these circumstances, the Committee believes that, against the background of its long-run goals of price stability and sustainable economic growth and of the information currently available, the risks are balanced with respect to the prospects for both goals for the foreseeable future.

## 7. 2003-01-29  (previous: 2002-12-10)

- removed: The Committee continues to believe that this accommodative stance of monetary policy, coupled with still robust underlying growth in productivity, is providing important ongoing support to economic activity.
- removed: The limited number of incoming economic indicators since the November meeting, taken together, are not inconsistent with the economy working its way through its current soft spot.
+ added: Oil price premiums and other aspects of geopolitical risks have reportedly fostered continued restraint on spending and hiring by businesses.
+ added: However, the Committee believes that as those risks lift, as most analysts expect, the accommodative stance of monetary policy, coupled with ongoing growth in productivity, will provide support to an improving economic climate over time.

## 8. 2003-08-12  (previous: 2003-06-25)

- removed: The Federal Open Market Committee decided today to lower its target for the federal funds rate by 25 basis points to 1 percent.
- removed: In a related action, the Board of Governors approved a 25 basis point reduction in the discount rate to 2 percent.
- removed: The Committee continues to believe that an accommodative stance of monetary policy, coupled with still robust underlying growth in productivity, is providing important ongoing support to economic activity.
- removed: Recent signs point to a firming in spending, markedly improved financial conditions, and labor and product markets that are stabilizing.
- removed: The economy, nonetheless, has yet to exhibit sustainable growth.
- removed: With inflationary expectations subdued, the Committee judged that a slightly more expansive monetary policy would add further support for an economy which it expects to improve over time.
+ added: The Federal Open Market Committee decided today to keep its target for the federal funds rate at 1 percent.
+ added: The Committee continues to believe that an accommodative stance of monetary policy, coupled with still-robust underlying growth in productivity, is providing important ongoing support to economic activity.
+ added: The evidence accumulated over the intermeeting period shows that spending is firming, although labor market indicators are mixed.
+ added: Business pricing power and increases in core consumer prices remain muted.
- removed: In contrast, the probability, though minor, of an unwelcome substantial fall in inflation exceeds that of a pickup in inflation from its already low level.
- removed: On balance, the Committee believes that the latter concern is likely to predominate for the foreseeable future.
+ added: In contrast, the probability, though minor, of an unwelcome fall in inflation exceeds that of a rise in inflation from its already low level.
+ added: The Committee judges that, on balance, the risk of inflation becoming undesirably low is likely to be the predominant concern for the foreseeable future.
+ added: In these circumstances, the Committee believes that policy accommodation can be maintained for a considerable period.

## 9. 2003-10-28  (previous: 2003-09-16)

- removed: The evidence accumulated over the intermeeting period confirms that spending is firming, although the labor market has been weakening.
+ added: The evidence accumulated over the intermeeting period confirms that spending is firming, and the labor market appears to be stabilizing.

## 10. 2003-12-09  (previous: 2003-10-28)

- removed: The evidence accumulated over the intermeeting period confirms that spending is firming, and the labor market appears to be stabilizing.
- removed: Business pricing power and increases in core consumer prices remain muted.
+ added: The evidence accumulated over the intermeeting period confirms that output is expanding briskly, and the labor market appears to be improving modestly.
+ added: Increases in core consumer prices are muted and expected to remain low.
- removed: In contrast, the probability, though minor, of an unwelcome fall in inflation exceeds that of a rise in inflation from its already low level.
- removed: The Committee judges that, on balance, the risk of inflation becoming undesirably low remains the predominant concern for the foreseeable future.
- removed: In these circumstances, the Committee believes that policy accommodation can be maintained for a considerable period.
+ added: The probability of an unwelcome fall in inflation has diminished in recent months and now appears almost equal to that of a rise in inflation.
+ added: However, with inflation quite low and resource use slack, the Committee believes that policy accommodation can be maintained for a considerable period.

## 11. 2007-03-21  (previous: 2007-01-31)

- removed: Recent indicators have suggested somewhat firmer economic growth, and some tentative signs of stabilization have appeared in the housing market.
- removed: Overall, the economy seems likely to expand at a moderate pace over coming quarters.
- removed: Readings on core inflation have improved modestly in recent months, and inflation pressures seem likely to moderate over time.
- removed: However, the high level of resource utilization has the potential to sustain inflation pressures.
- removed: The Committee judges that some inflation risks remain.
- removed: The extent and timing of any additional firming that may be needed to address these risks will depend on the evolution of the outlook for both inflation and economic growth, as implied by incoming information.
+ added: Recent indicators have been mixed and the adjustment in the housing sector is ongoing.
+ added: Nevertheless, the economy seems likely to continue to expand at a moderate pace over coming quarters.
+ added: Recent readings on core inflation have been somewhat elevated.
+ added: Although inflation pressures seem likely to moderate over time, the high level of resource utilization has the potential to sustain those pressures.
+ added: In these circumstances, the Committee's predominant policy concern remains the risk that inflation will fail to moderate as expected.
+ added: Future policy adjustments will depend on the evolution of the outlook for both inflation and economic growth, as implied by incoming information.

## 12. 2007-05-09  (previous: 2007-03-21)

- removed: Recent indicators have been mixed and the adjustment in the housing sector is ongoing.
- removed: Nevertheless, the economy seems likely to continue to expand at a moderate pace over coming quarters.
- removed: Recent readings on core inflation have been somewhat elevated.
+ added: Economic growth slowed in the first part of this year and the adjustment in the housing sector is ongoing.
+ added: Nevertheless, the economy seems likely to expand at a moderate pace over coming quarters.
+ added: Core inflation remains somewhat elevated.

## 13. 2007-08-07  (previous: 2007-06-28)

- removed: Economic growth appears to have been moderate during the first half of this year, despite the ongoing adjustment in the housing sector.
- removed: The economy seems likely to continue to expand at a moderate pace over coming quarters.
+ added: Economic growth was moderate during the first half of the year.
+ added: Financial markets have been volatile in recent weeks, credit conditions have become tighter for some households and businesses, and the housing correction is ongoing.
+ added: Nevertheless, the economy seems likely to continue to expand at a moderate pace over coming quarters, supported by solid growth in employment and incomes and a robust global economy.
- removed: In these circumstances, the Committee's predominant policy concern remains the risk that inflation will fail to moderate as expected.
- removed: Future policy adjustments will depend on the evolution of the outlook for both inflation and economic growth, as implied by incoming information.
+ added: Although the downside risks to growth have increased somewhat, the Committee's predominant policy concern remains the risk that inflation will fail to moderate as expected.
+ added: Future policy adjustments will depend on the outlook for both inflation and economic growth, as implied by incoming information.

## 14. 2009-06-24  (previous: 2009-04-29)

- removed: Information received since the Federal Open Market Committee met in March indicates that the economy has continued to contract, though the pace of contraction appears to be somewhat slower.
- removed: Household spending has shown signs of stabilizing but remains constrained by ongoing job losses, lower housing wealth, and tight credit.
- removed: Weak sales prospects and difficulties in obtaining credit have led businesses to cut back on inventories, fixed investment, and staffing.
- removed: Although the economic outlook has improved modestly since the March meeting, partly reflecting some easing of financial market conditions, economic activity is likely to remain weak for a time.
- removed: Nonetheless, the Committee continues to anticipate that policy actions to stabilize financial markets and institutions, fiscal and monetary stimulus, and market forces will contribute to a gradual resumption of sustainable economic growth in a context of price stability.
- removed: In light of increasing economic slack here and abroad, the Committee expects that inflation will remain subdued.
- removed: Moreover, the Committee sees some risk that inflation could persist for a time below rates that best foster economic growth and price stability in the longer term.
+ added: Information received since the Federal Open Market Committee met in April suggests that the pace of economic contraction is slowing.
+ added: Conditions in financial markets have generally improved in recent months.
+ added: Household spending has shown further signs of stabilizing but remains constrained by ongoing job losses, lower housing wealth, and tight credit.
+ added: Businesses are cutting back on fixed investment and staffing but appear to be making progress in bringing inventory stocks into better alignment with sales.
+ added: Although economic activity is likely to remain weak for a time, the Committee continues to anticipate that policy actions to stabilize financial markets and institutions, fiscal and monetary stimulus, and market forces will contribute to a gradual resumption of sustainable economic growth in a context of price stability.
+ added: The prices of energy and other commodities have risen of late.
+ added: However, substantial resource slack is likely to dampen cost pressures, and the Committee expects that inflation will remain subdued for some time.
- removed: The Committee will maintain the target range for the federal funds rate at 0 to 1/4 percent and anticipates that economic conditions are likely to warrant exceptionally low levels of the federal funds rate for an extended period.
+ added: The Committee will maintain the target range for the federal funds rate at 0 to 1/4 percent and continues to anticipate that economic conditions are likely to warrant exceptionally low levels of the federal funds rate for an extended period.
- removed: The Federal Reserve is facilitating the extension of credit to households and businesses and supporting the functioning of financial markets through a range of liquidity programs.
- removed: The Committee will continue to carefully monitor the size and composition of the Federal Reserve's balance sheet in light of financial and economic developments.
+ added: The Federal Reserve is monitoring the size and composition of its balance sheet and will make adjustments to its credit and liquidity programs as warranted.

## 15. 2010-06-23  (previous: 2010-04-28)

- removed: Information received since the Federal Open Market Committee met in March suggests that economic activity has continued to strengthen and that the labor market is beginning to improve.
- removed: Growth in household spending has picked up recently but remains constrained by high unemployment, modest income growth, lower housing wealth, and tight credit.
- removed: Business spending on equipment and software has risen significantly; however, investment in nonresidential structures is declining and employers remain reluctant to add to payrolls.
- removed: Housing starts have edged up but remain at a depressed level.
- removed: While bank lending continues to contract, financial market conditions remain supportive of economic growth.
- removed: Although the pace of economic recovery is likely to be moderate for a time, the Committee anticipates a gradual return to higher levels of resource utilization in a context of price stability.
+ added: Information received since the Federal Open Market Committee met in April suggests that the economic recovery is proceeding and that the labor market is improving gradually.
+ added: Household spending is increasing but remains constrained by high unemployment, modest income growth, lower housing wealth, and tight credit.
+ added: Business spending on equipment and software has risen significantly; however, investment in nonresidential structures continues to be weak and employers remain reluctant to add to payrolls.
+ added: Housing starts remain at a depressed level.
+ added: Financial conditions have become less supportive of economic growth on balance, largely reflecting developments abroad.
+ added: Bank lending has continued to contract in recent months.
+ added: Nonetheless, the Committee anticipates a gradual return to higher levels of resource utilization in a context of price stability, although the pace of economic recovery is likely to be moderate for a time.
+ added: Prices of energy and other commodities have declined somewhat in recent months, and underlying inflation has trended lower.
- removed: In light of improved functioning of financial markets, the Federal Reserve has closed all but one of the special liquidity facilities that it created to support markets during the crisis.
- removed: The only remaining such program, the Term Asset-Backed Securities Loan Facility, is scheduled to close on June 30 for loans backed by new-issue commercial mortgage-backed securities; it closed on March 31 for loans backed by all other types of collateral.

## 16. 2010-12-14  (previous: 2010-11-03)

- removed: Information received since the Federal Open Market Committee met in September confirms that the pace of recovery in output and employment continues to be slow.
- removed: Household spending is increasing gradually, but remains constrained by high unemployment, modest income growth, lower housing wealth, and tight credit.
+ added: Information received since the Federal Open Market Committee met in November confirms that the economic recovery is continuing, though at a rate that has been insufficient to bring down unemployment.
+ added: Household spending is increasing at a moderate pace, but remains constrained by high unemployment, modest income growth, lower housing wealth, and tight credit.
- removed: Housing starts continue to be depressed.
- removed: Longer-term inflation expectations have remained stable, but measures of underlying inflation have trended lower in recent quarters.
+ added: The housing sector continues to be depressed.
+ added: Longer-term inflation expectations have remained stable, but measures of underlying inflation have continued to trend downward.
- removed: To promote a stronger pace of economic recovery and to help ensure that inflation, over time, is at levels consistent with its mandate, the Committee decided today to expand its holdings of securities.
+ added: To promote a stronger pace of economic recovery and to help ensure that inflation, over time, is at levels consistent with its mandate, the Committee decided today to continue expanding its holdings of securities as announced in November.
- removed: In addition, the Committee intends to purchase a further $600 billion of longer-term Treasury securities by the end of the second quarter of 2011, a pace of about $75 billion per month.
+ added: In addition, the Committee intends to purchase $600 billion of longer-term Treasury securities by the end of the second quarter of 2011, a pace of about $75 billion per month.

## 17. 2011-04-27  (previous: 2011-03-15)

- removed: Information received since the Federal Open Market Committee met in January suggests that the economic recovery is on a firmer footing, and overall conditions in the labor market appear to be improving gradually.
+ added: Information received since the Federal Open Market Committee met in March indicates that the economic recovery is proceeding at a moderate pace and overall conditions in the labor market are improving gradually.
- removed: Commodity prices have risen significantly since the summer, and concerns about global supplies of crude oil have contributed to a sharp run-up in oil prices in recent weeks.
- removed: Nonetheless, longer-term inflation expectations have remained stable, and measures of underlying inflation have been subdued.
+ added: Commodity prices have risen significantly since last summer, and concerns about global supplies of crude oil have contributed to a further increase in oil prices since the Committee met in March.
+ added: Inflation has picked up in recent months, but longer-term inflation expectations have remained stable and measures of underlying inflation are still subdued.
- removed: Currently, the unemployment rate remains elevated, and measures of underlying inflation continue to be somewhat low, relative to levels that the Committee judges to be consistent, over the longer run, with its dual mandate.
- removed: The recent increases in the prices of energy and other commodities are currently putting upward pressure on inflation.
+ added: The unemployment rate remains elevated, and measures of underlying inflation continue to be somewhat low, relative to levels that the Committee judges to be consistent, over the longer run, with its dual mandate.
+ added: Increases in the prices of energy and other commodities have pushed up inflation in recent months.
- removed: In particular, the Committee is maintaining its existing policy of reinvesting principal payments from its securities holdings and intends to purchase $600 billion of longer-term Treasury securities by the end of the second quarter of 2011.
- removed: The Committee will regularly review the pace of its securities purchases and the overall size of the asset-purchase program in light of incoming information and will adjust the program as needed to best foster maximum employment and price stability.
+ added: In particular, the Committee is maintaining its existing policy of reinvesting principal payments from its securities holdings and will complete purchases of $600 billion of longer-term Treasury securities by the end of the current quarter.
+ added: The Committee will regularly review the size and composition of its securities holdings in light of incoming information and is prepared to adjust those holdings as needed to best foster maximum employment and price stability.

## 18. 2011-06-22  (previous: 2011-04-27)

- removed: Information received since the Federal Open Market Committee met in March indicates that the economic recovery is proceeding at a moderate pace and overall conditions in the labor market are improving gradually.
+ added: Information received since the Federal Open Market Committee met in April indicates that the economic recovery is continuing at a moderate pace, though somewhat more slowly than the Committee had expected.
+ added: Also, recent labor market indicators have been weaker than anticipated.
+ added: The slower pace of the recovery reflects in part factors that are likely to be temporary, including the damping effect of higher food and energy prices on consumer purchasing power and spending as well as supply chain disruptions associated with the tragic events in Japan.
- removed: Commodity prices have risen significantly since last summer, and concerns about global supplies of crude oil have contributed to a further increase in oil prices since the Committee met in March.
- removed: Inflation has picked up in recent months, but longer-term inflation expectations have remained stable and measures of underlying inflation are still subdued.
+ added: Inflation has picked up in recent months, mainly reflecting higher prices for some commodities and imported goods, as well as the recent supply chain disruptions.
+ added: However, longer-term inflation expectations have remained stable.
- removed: The unemployment rate remains elevated, and measures of underlying inflation continue to be somewhat low, relative to levels that the Committee judges to be consistent, over the longer run, with its dual mandate.
- removed: Increases in the prices of energy and other commodities have pushed up inflation in recent months.
- removed: The Committee expects these effects to be transitory, but it will pay close attention to the evolution of inflation and inflation expectations.
- removed: The Committee continues to anticipate a gradual return to higher levels of resource utilization in a context of price stability.
- removed: To promote a stronger pace of economic recovery and to help ensure that inflation, over time, is at levels consistent with its mandate, the Committee decided today to continue expanding its holdings of securities as announced in November.
- removed: In particular, the Committee is maintaining its existing policy of reinvesting principal payments from its securities holdings and will complete purchases of $600 billion of longer-term Treasury securities by the end of the current quarter.
- removed: The Committee will regularly review the size and composition of its securities holdings in light of incoming information and is prepared to adjust those holdings as needed to best foster maximum employment and price stability.
- removed: The Committee will maintain the target range for the federal funds rate at 0 to 1/4 percent and continues to anticipate that economic conditions, including low rates of resource utilization, subdued inflation trends, and stable inflation expectations, are likely to warrant exceptionally low levels for the federal funds rate for an extended period.
- removed: The Committee will continue to monitor the economic outlook and financial developments and will employ its policy tools as necessary to support the economic recovery and to help ensure that inflation, over time, is at levels consistent with its mandate.
+ added: The unemployment rate remains elevated; however, the Committee expects the pace of recovery to pick up over coming quarters and the unemployment rate to resume its gradual decline toward levels that the Committee judges to be consistent with its dual mandate.
+ added: Inflation has moved up recently, but the Committee anticipates that inflation will subside to levels at or below those consistent with the Committee's dual mandate as the effects of past energy and other commodity price increases dissipate.
+ added: However, the Committee will continue to pay close attention to the evolution of inflation and inflation expectations.
+ added: To promote the ongoing economic recovery and to help ensure that inflation, over time, is at levels consistent with its mandate, the Committee decided today to keep the target range for the federal funds rate at 0 to 1/4 percent.
+ added: The Committee continues to anticipate that economic conditions--including low rates of resource utilization and a subdued outlook for inflation over the medium run--are likely to warrant exceptionally low levels for the federal funds rate for an extended period.
+ added: The Committee will complete its purchases of $600 billion of longer-term Treasury securities by the end of this month and will maintain its existing policy of reinvesting principal payments from its securities holdings.
+ added: The Committee will regularly review the size and composition of its securities holdings and is prepared to adjust those holdings as appropriate.
+ added: The Committee will monitor the economic outlook and financial developments and will act as needed to best foster maximum employment and price stability.

## 19. 2011-08-09  (previous: 2011-06-22)

- removed: Information received since the Federal Open Market Committee met in April indicates that the economic recovery is continuing at a moderate pace, though somewhat more slowly than the Committee had expected.
- removed: Also, recent labor market indicators have been weaker than anticipated.
- removed: The slower pace of the recovery reflects in part factors that are likely to be temporary, including the damping effect of higher food and energy prices on consumer purchasing power and spending as well as supply chain disruptions associated with the tragic events in Japan.
- removed: Household spending and business investment in equipment and software continue to expand.
- removed: However, investment in nonresidential structures is still weak, and the housing sector continues to be depressed.
- removed: Inflation has picked up in recent months, mainly reflecting higher prices for some commodities and imported goods, as well as the recent supply chain disruptions.
- removed: However, longer-term inflation expectations have remained stable.
+ added: Information received since the Federal Open Market Committee met in June indicates that economic growth so far this year has been considerably slower than the Committee had expected.
+ added: Indicators suggest a deterioration in overall labor market conditions in recent months, and the unemployment rate has moved up.
+ added: Household spending has flattened out, investment in nonresidential structures is still weak, and the housing sector remains depressed.
+ added: However, business investment in equipment and software continues to expand.
+ added: Temporary factors, including the damping effect of higher food and energy prices on consumer purchasing power and spending as well as supply chain disruptions associated with the tragic events in Japan, appear to account for only some of the recent weakness in economic activity.
+ added: Inflation picked up earlier in the year, mainly reflecting higher prices for some commodities and imported goods, as well as the supply chain disruptions.
+ added: More recently, inflation has moderated as prices of energy and some commodities have declined from their earlier peaks.
+ added: Longer-term inflation expectations have remained stable.
- removed: The unemployment rate remains elevated; however, the Committee expects the pace of recovery to pick up over coming quarters and the unemployment rate to resume its gradual decline toward levels that the Committee judges to be consistent with its dual mandate.
- removed: Inflation has moved up recently, but the Committee anticipates that inflation will subside to levels at or below those consistent with the Committee's dual mandate as the effects of past energy and other commodity price increases dissipate.
+ added: The Committee now expects a somewhat slower pace of recovery over coming quarters than it did at the time of the previous meeting and anticipates that the unemployment rate will decline only gradually toward levels that the Committee judges to be consistent with its dual mandate.
+ added: Moreover, downside risks to the economic outlook have increased.
+ added: The Committee also anticipates that inflation will settle, over coming quarters, at levels at or below those consistent with the Committee's dual mandate as the effects of past energy and other commodity price increases dissipate further.
- removed: The Committee continues to anticipate that economic conditions--including low rates of resource utilization and a subdued outlook for inflation over the medium run--are likely to warrant exceptionally low levels for the federal funds rate for an extended period.
- removed: The Committee will complete its purchases of $600 billion of longer-term Treasury securities by the end of this month and will maintain its existing policy of reinvesting principal payments from its securities holdings.
+ added: The Committee currently anticipates that economic conditions--including low rates of resource utilization and a subdued outlook for inflation over the medium run--are likely to warrant exceptionally low levels for the federal funds rate at least through mid-2013.
+ added: The Committee also will maintain its existing policy of reinvesting principal payments from its securities holdings.
- removed: The Committee will monitor the economic outlook and financial developments and will act as needed to best foster maximum employment and price stability.
+ added: The Committee discussed the range of policy tools available to promote a stronger economic recovery in a context of price stability.
+ added: It will continue to assess the economic outlook in light of incoming information and is prepared to employ these tools as appropriate.

## 20. 2012-09-13  (previous: 2012-08-01)

- removed: Information received since the Federal Open Market Committee met in June suggests that economic activity decelerated somewhat over the first half of this year.
- removed: Growth in employment has been slow in recent months, and the unemployment rate remains elevated.
- removed: Business fixed investment has continued to advance.
- removed: Household spending has been rising at a somewhat slower pace than earlier in the year.
- removed: Despite some further signs of improvement, the housing sector remains depressed.
- removed: Inflation has declined since earlier this year, mainly reflecting lower prices of crude oil and gasoline, and longer-term inflation expectations have remained stable.
+ added: Information received since the Federal Open Market Committee met in August suggests that economic activity has continued to expand at a moderate pace in recent months.
+ added: Growth in employment has been slow, and the unemployment rate remains elevated.
+ added: Household spending has continued to advance, but growth in business fixed investment appears to have slowed.
+ added: The housing sector has shown some further signs of improvement, albeit from a depressed level.
+ added: Inflation has been subdued, although the prices of some key commodities have increased recently.
+ added: Longer-term inflation expectations have remained stable.
- removed: The Committee expects economic growth to remain moderate over coming quarters and then to pick up very gradually.
- removed: Consequently, the Committee anticipates that the unemployment rate will decline only slowly toward levels that it judges to be consistent with its dual mandate.
+ added: The Committee is concerned that, without further policy accommodation, economic growth might not be strong enough to generate sustained improvement in labor market conditions.
- removed: The Committee anticipates that inflation over the medium term will run at or below the rate that it judges most consistent with its dual mandate.
- removed: To support a stronger economic recovery and to help ensure that inflation, over time, is at the rate most consistent with its dual mandate, the Committee expects to maintain a highly accommodative stance for monetary policy.
- removed: In particular, the Committee decided today to keep the target range for the federal funds rate at 0 to 1/4 percent and currently anticipates that economic conditions--including low rates of resource utilization and a subdued outlook for inflation over the medium run--are likely to warrant exceptionally low levels for the federal funds rate at least through late 2014.
- removed: The Committee also decided to continue through the end of the year its program to extend the average maturity of its holdings of securities as announced in June, and it is maintaining its existing policy of reinvesting principal payments from its holdings of agency debt and agency mortgage-backed securities in agency mortgage-backed securities.
- removed: The Committee will closely monitor incoming information on economic and financial developments and will provide additional accommodation as needed to promote a stronger economic recovery and sustained improvement in labor market conditions in a context of price stability.
+ added: The Committee also anticipates that inflation over the medium term likely would run at or below its 2 percent objective.
+ added: To support a stronger economic recovery and to help ensure that inflation, over time, is at the rate most consistent with its dual mandate, the Committee agreed today to increase policy accommodation by purchasing additional agency mortgage-backed securities at a pace of $40 billion per month.
+ added: The Committee also will continue through the end of the year its program to extend the average maturity of its holdings of securities as announced in June, and it is maintaining its existing policy of reinvesting principal payments from its holdings of agency debt and agency mortgage-backed securities in agency mortgage-backed securities.
+ added: These actions, which together will increase the Committee’s holdings of longer-term securities by about $85 billion each month through the end of the year, should put downward pressure on longer-term interest rates, support mortgage markets, and help to make broader financial conditions more accommodative.
+ added: The Committee will closely monitor incoming information on economic and financial developments in coming months.
+ added: If the outlook for the labor market does not improve substantially, the Committee will continue its purchases of agency mortgage-backed securities, undertake additional asset purchases, and employ its other policy tools as appropriate until such improvement is achieved in a context of price stability.
+ added: In determining the size, pace, and composition of its asset purchases, the Committee will, as always, take appropriate account of the likely efficacy and costs of such purchases.
+ added: To support continued progress toward maximum employment and price stability, the Committee expects that a highly accommodative stance of monetary policy will remain appropriate for a considerable time after the economic recovery strengthens.
+ added: In particular, the Committee also decided today to keep the target range for the federal funds rate at 0 to 1/4 percent and currently anticipates that exceptionally low levels for the federal funds rate are likely to be warranted at least through mid-2015.

## 21. 2013-03-20  (previous: 2013-01-30)

- removed: Information received since the Federal Open Market Committee met in December suggests that growth in economic activity paused in recent months, in large part because of weather-related disruptions and other transitory factors.
- removed: Employment has continued to expand at a moderate pace but the unemployment rate remains elevated.
- removed: Household spending and business fixed investment advanced, and the housing sector has shown further improvement.
- removed: Inflation has been running somewhat below the Committee’s longer-run objective, apart from temporary variations that largely reflect fluctuations in energy prices.
+ added: Information received since the Federal Open Market Committee met in January suggests a return to moderate economic growth following a pause late last year.
+ added: Labor market conditions have shown signs of improvement in recent months but the unemployment rate remains elevated.
+ added: Household spending and business fixed investment advanced, and the housing sector has strengthened further, but fiscal policy has become somewhat more restrictive.
+ added: Inflation has been running somewhat below the Committee's longer-run objective, apart from temporary variations that largely reflect fluctuations in energy prices.
- removed: Although strains in global financial markets have eased somewhat, the Committee continues to see downside risks to the economic outlook.
+ added: The Committee continues to see downside risks to the economic outlook.
- removed: To support a stronger economic recovery and to help ensure that inflation, over time, is at the rate most consistent with its dual mandate, the Committee will continue purchasing additional agency mortgage-backed securities at a pace of $40 billion per month and longer-term Treasury securities at a pace of $45 billion per month.
+ added: To support a stronger economic recovery and to help ensure that inflation, over time, is at the rate most consistent with its dual mandate, the Committee decided to continue purchasing additional agency mortgage-backed securities at a pace of $40 billion per month and longer-term Treasury securities at a pace of $45 billion per month.
- removed: If the outlook for the labor market does not improve substantially, the Committee will continue its purchases of Treasury and agency mortgage-backed securities, and employ its other policy tools as appropriate, until such improvement is achieved in a context of price stability.
- removed: In determining the size, pace, and composition of its asset purchases, the Committee will, as always, take appropriate account of the likely efficacy and costs of such purchases.
+ added: The Committee will continue its purchases of Treasury and agency mortgage-backed securities, and employ its other policy tools as appropriate, until the outlook for the labor market has improved substantially in a context of price stability.
+ added: In determining the size, pace, and composition of its asset purchases, the Committee will continue to take appropriate account of the likely efficacy and costs of such purchases as well as the extent of progress toward its economic objectives.
- removed: In particular, the Committee decided to keep the target range for the federal funds rate at 0 to 1/4 percent and currently anticipates that this exceptionally low range for the federal funds rate will be appropriate at least as long as the unemployment rate remains above 6-1/2 percent, inflation between one and two years ahead is projected to be no more than a half percentage point above the Committee’s 2 percent longer-run goal, and longer-term inflation expectations continue to be well anchored.
+ added: In particular, the Committee decided to keep the target range for the federal funds rate at 0 to 1/4 percent and currently anticipates that this exceptionally low range for the federal funds rate will be appropriate at least as long as the unemployment rate remains above 6-1/2 percent, inflation between one and two years ahead is projected to be no more than a half percentage point above the Committee's 2 percent longer-run goal, and longer-term inflation expectations continue to be well anchored.

## 22. 2013-06-19  (previous: 2013-05-01)

- removed: Information received since the Federal Open Market Committee met in March suggests that economic activity has been expanding at a moderate pace.
- removed: Labor market conditions have shown some improvement in recent months, on balance, but the unemployment rate remains elevated.
+ added: Information received since the Federal Open Market Committee met in May suggests that economic activity has been expanding at a moderate pace.
+ added: Labor market conditions have shown further improvement in recent months, on balance, but the unemployment rate remains elevated.
- removed: Inflation has been running somewhat below the Committee's longer-run objective, apart from temporary variations that largely reflect fluctuations in energy prices.
- removed: Longer-term inflation expectations have remained stable.
+ added: Partly reflecting transitory influences, inflation has been running below the Committee's longer-run objective, but longer-term inflation expectations have remained stable.
- removed: The Committee continues to see downside risks to the economic outlook.
+ added: The Committee sees the downside risks to the outlook for the economy and the labor market as having diminished since the fall.

## 23. 2013-07-31  (previous: 2013-06-19)

- removed: Information received since the Federal Open Market Committee met in May suggests that economic activity has been expanding at a moderate pace.
+ added: Information received since the Federal Open Market Committee met in June suggests that economic activity expanded at a modest pace during the first half of the year.
- removed: Household spending and business fixed investment advanced, and the housing sector has strengthened further, but fiscal policy is restraining economic growth.
+ added: Household spending and business fixed investment advanced, and the housing sector has been strengthening, but mortgage rates have risen somewhat and fiscal policy is restraining economic growth.
- removed: The Committee expects that, with appropriate policy accommodation, economic growth will proceed at a moderate pace and the unemployment rate will gradually decline toward levels the Committee judges consistent with its dual mandate.
+ added: The Committee expects that, with appropriate policy accommodation, economic growth will pick up from its recent pace and the unemployment rate will gradually decline toward levels the Committee judges consistent with its dual mandate.
- removed: The Committee also anticipates that inflation over the medium term likely will run at or below its 2 percent objective.
+ added: The Committee recognizes that inflation persistently below its 2 percent objective could pose risks to economic performance, but it anticipates that inflation will move back toward its objective over the medium term.
- removed: To support continued progress toward maximum employment and price stability, the Committee expects that a highly accommodative stance of monetary policy will remain appropriate for a considerable time after the asset purchase program ends and the economic recovery strengthens.
+ added: To support continued progress toward maximum employment and price stability, the Committee today reaffirmed its view that a highly accommodative stance of monetary policy will remain appropriate for a considerable time after the asset purchase program ends and the economic recovery strengthens.

## 24. 2013-09-18  (previous: 2013-07-31)

- removed: Information received since the Federal Open Market Committee met in June suggests that economic activity expanded at a modest pace during the first half of the year.
- removed: Labor market conditions have shown further improvement in recent months, on balance, but the unemployment rate remains elevated.
- removed: Household spending and business fixed investment advanced, and the housing sector has been strengthening, but mortgage rates have risen somewhat and fiscal policy is restraining economic growth.
- removed: Partly reflecting transitory influences, inflation has been running below the Committee's longer-run objective, but longer-term inflation expectations have remained stable.
+ added: Information received since the Federal Open Market Committee met in July suggests that economic activity has been expanding at a moderate pace.
+ added: Some indicators of labor market conditions have shown further improvement in recent months, but the unemployment rate remains elevated.
+ added: Household spending and business fixed investment advanced, and the housing sector has been strengthening, but mortgage rates have risen further and fiscal policy is restraining economic growth.
+ added: Apart from fluctuations due to changes in energy prices, inflation has been running below the Committee's longer-run objective, but longer-term inflation expectations have remained stable.
- removed: The Committee sees the downside risks to the outlook for the economy and the labor market as having diminished since the fall.
+ added: The Committee sees the downside risks to the outlook for the economy and the labor market as having diminished, on net, since last fall, but the tightening of financial conditions observed in recent months, if sustained, could slow the pace of improvement in the economy and labor market.
- removed: To support a stronger economic recovery and to help ensure that inflation, over time, is at the rate most consistent with its dual mandate, the Committee decided to continue purchasing additional agency mortgage-backed securities at a pace of $40 billion per month and longer-term Treasury securities at a pace of $45 billion per month.
+ added: Taking into account the extent of federal fiscal retrenchment, the Committee sees the improvement in economic activity and labor market conditions since it began its asset purchase program a year ago as consistent with growing underlying strength in the broader economy.
+ added: However, the Committee decided to await more evidence that progress will be sustained before adjusting the pace of its purchases.
+ added: Accordingly, the Committee decided to continue purchasing additional agency mortgage-backed securities at a pace of $40 billion per month and longer-term Treasury securities at a pace of $45 billion per month.
- removed: Taken together, these actions should maintain downward pressure on longer-term interest rates, support mortgage markets, and help to make broader financial conditions more accommodative.
- removed: The Committee will closely monitor incoming information on economic and financial developments in coming months.
- removed: The Committee will continue its purchases of Treasury and agency mortgage-backed securities, and employ its other policy tools as appropriate, until the outlook for the labor market has improved substantially in a context of price stability.
- removed: The Committee is prepared to increase or reduce the pace of its purchases to maintain appropriate policy accommodation as the outlook for the labor market or inflation changes.
- removed: In determining the size, pace, and composition of its asset purchases, the Committee will continue to take appropriate account of the likely efficacy and costs of such purchases as well as the extent of progress toward its economic objectives.
+ added: Taken together, these actions should maintain downward pressure on longer-term interest rates, support mortgage markets, and help to make broader financial conditions more accommodative, which in turn should promote a stronger economic recovery and help to ensure that inflation, over time, is at the rate most consistent with the Committee's dual mandate.
+ added: The Committee will closely monitor incoming information on economic and financial developments in coming months and will continue its purchases of Treasury and agency mortgage-backed securities, and employ its other policy tools as appropriate, until the outlook for the labor market has improved substantially in a context of price stability.
+ added: In judging when to moderate the pace of asset purchases, the Committee will, at its coming meetings, assess whether incoming information continues to support the Committee's expectation of ongoing improvement in labor market conditions and inflation moving back toward its longer-run objective.
+ added: Asset purchases are not on a preset course, and the Committee's decisions about their pace will remain contingent on the Committee's economic outlook as well as its assessment of the likely efficacy and costs of such purchases.

## 25. 2013-10-30  (previous: 2013-09-18)

- removed: Information received since the Federal Open Market Committee met in July suggests that economic activity has been expanding at a moderate pace.
- removed: Some indicators of labor market conditions have shown further improvement in recent months, but the unemployment rate remains elevated.
- removed: Household spending and business fixed investment advanced, and the housing sector has been strengthening, but mortgage rates have risen further and fiscal policy is restraining economic growth.
+ added: Information received since the Federal Open Market Committee met in September generally suggests that economic activity has continued to expand at a moderate pace.
+ added: Indicators of labor market conditions have shown some further improvement, but the unemployment rate remains elevated.
+ added: Available data suggest that household spending and business fixed investment advanced, while the recovery in the housing sector slowed somewhat in recent months.
+ added: Fiscal policy is restraining economic growth.
- removed: The Committee sees the downside risks to the outlook for the economy and the labor market as having diminished, on net, since last fall, but the tightening of financial conditions observed in recent months, if sustained, could slow the pace of improvement in the economy and labor market.
+ added: The Committee sees the downside risks to the outlook for the economy and the labor market as having diminished, on net, since last fall.
- removed: Taking into account the extent of federal fiscal retrenchment, the Committee sees the improvement in economic activity and labor market conditions since it began its asset purchase program a year ago as consistent with growing underlying strength in the broader economy.
+ added: Taking into account the extent of federal fiscal retrenchment over the past year, the Committee sees the improvement in economic activity and labor market conditions since it began its asset purchase program as consistent with growing underlying strength in the broader economy.

## 26. 2013-12-18  (previous: 2013-10-30)

- removed: Information received since the Federal Open Market Committee met in September generally suggests that economic activity has continued to expand at a moderate pace.
- removed: Indicators of labor market conditions have shown some further improvement, but the unemployment rate remains elevated.
- removed: Available data suggest that household spending and business fixed investment advanced, while the recovery in the housing sector slowed somewhat in recent months.
- removed: Fiscal policy is restraining economic growth.
- removed: Apart from fluctuations due to changes in energy prices, inflation has been running below the Committee's longer-run objective, but longer-term inflation expectations have remained stable.
+ added: Information received since the Federal Open Market Committee met in October indicates that economic activity is expanding at a moderate pace.
+ added: Labor market conditions have shown further improvement; the unemployment rate has declined but remains elevated.
+ added: Household spending and business fixed investment advanced, while the recovery in the housing sector slowed somewhat in recent months.
+ added: Fiscal policy is restraining economic growth, although the extent of restraint may be diminishing.
+ added: Inflation has been running below the Committee's longer-run objective, but longer-term inflation expectations have remained stable.
- removed: The Committee sees the downside risks to the outlook for the economy and the labor market as having diminished, on net, since last fall.
- removed: The Committee recognizes that inflation persistently below its 2 percent objective could pose risks to economic performance, but it anticipates that inflation will move back toward its objective over the medium term.
- removed: Taking into account the extent of federal fiscal retrenchment over the past year, the Committee sees the improvement in economic activity and labor market conditions since it began its asset purchase program as consistent with growing underlying strength in the broader economy.
- removed: However, the Committee decided to await more evidence that progress will be sustained before adjusting the pace of its purchases.
- removed: Accordingly, the Committee decided to continue purchasing additional agency mortgage-backed securities at a pace of $40 billion per month and longer-term Treasury securities at a pace of $45 billion per month.
+ added: The Committee sees the risks to the outlook for the economy and the labor market as having become more nearly balanced.
+ added: The Committee recognizes that inflation persistently below its 2 percent objective could pose risks to economic performance, and it is monitoring inflation developments carefully for evidence that inflation will move back toward its objective over the medium term.
+ added: Taking into account the extent of federal fiscal retrenchment since the inception of its current asset purchase program, the Committee sees the improvement in economic activity and labor market conditions over that period as consistent with growing underlying strength in the broader economy.
+ added: In light of the cumulative progress toward maximum employment and the improvement in the outlook for labor market conditions, the Committee decided to modestly reduce the pace of its asset purchases.
+ added: Beginning in January, the Committee will add to its holdings of agency mortgage-backed securities at a pace of $35 billion per month rather than $40 billion per month, and will add to its holdings of longer-term Treasury securities at a pace of $40 billion per month rather than $45 billion per month.
- removed: Taken together, these actions should maintain downward pressure on longer-term interest rates, support mortgage markets, and help to make broader financial conditions more accommodative, which in turn should promote a stronger economic recovery and help to ensure that inflation, over time, is at the rate most consistent with the Committee's dual mandate.
+ added: The Committee's sizable and still-increasing holdings of longer-term securities should maintain downward pressure on longer-term interest rates, support mortgage markets, and help to make broader financial conditions more accommodative, which in turn should promote a stronger economic recovery and help to ensure that inflation, over time, is at the rate most consistent with the Committee's dual mandate.
- removed: In judging when to moderate the pace of asset purchases, the Committee will, at its coming meetings, assess whether incoming information continues to support the Committee's expectation of ongoing improvement in labor market conditions and inflation moving back toward its longer-run objective.
- removed: Asset purchases are not on a preset course, and the Committee's decisions about their pace will remain contingent on the Committee's economic outlook as well as its assessment of the likely efficacy and costs of such purchases.
+ added: If incoming information broadly supports the Committee's expectation of ongoing improvement in labor market conditions and inflation moving back toward its longer-run objective, the Committee will likely reduce the pace of asset purchases in further measured steps at future meetings.
+ added: However, asset purchases are not on a preset course, and the Committee's decisions about their pace will remain contingent on the Committee's outlook for the labor market and inflation as well as its assessment of the likely efficacy and costs of such purchases.
- removed: In particular, the Committee decided to keep the target range for the federal funds rate at 0 to 1/4 percent and currently anticipates that this exceptionally low range for the federal funds rate will be appropriate at least as long as the unemployment rate remains above 6-1/2 percent, inflation between one and two years ahead is projected to be no more than a half percentage point above the Committee's 2 percent longer-run goal, and longer-term inflation expectations continue to be well anchored.
+ added: The Committee also reaffirmed its expectation that the current exceptionally low target range for the federal funds rate of 0 to 1/4 percent will be appropriate at least as long as the unemployment rate remains above 6-1/2 percent, inflation between one and two years ahead is projected to be no more than a half percentage point above the Committee's 2 percent longer-run goal, and longer-term inflation expectations continue to be well anchored.
+ added: The Committee now anticipates, based on its assessment of these factors, that it likely will be appropriate to maintain the current target range for the federal funds rate well past the time that the unemployment rate declines below 6-1/2 percent, especially if projected inflation continues to run below the Committee's 2 percent longer-run goal.

## 27. 2014-09-17  (previous: 2014-07-30)

- removed: Information received since the Federal Open Market Committee met in June indicates that growth in economic activity rebounded in the second quarter.
- removed: Labor market conditions improved, with the unemployment rate declining further.
- removed: However, a range of labor market indicators suggests that there remains significant underutilization of labor resources.
+ added: Information received since the Federal Open Market Committee met in July suggests that economic activity is expanding at a moderate pace.
+ added: On balance, labor market conditions improved somewhat further; however, the unemployment rate is little changed and a range of labor market indicators suggests that there remains significant underutilization of labor resources.
- removed: Inflation has moved somewhat closer to the Committee's longer-run objective.
+ added: Inflation has been running below the Committee's longer-run objective.
- removed: The Committee sees the risks to the outlook for economic activity and the labor market as nearly balanced and judges that the likelihood of inflation running persistently below 2 percent has diminished somewhat.
+ added: The Committee sees the risks to the outlook for economic activity and the labor market as nearly balanced and judges that the likelihood of inflation running persistently below 2 percent has diminished somewhat since early this year.
- removed: Beginning in August, the Committee will add to its holdings of agency mortgage-backed securities at a pace of $10 billion per month rather than $15 billion per month, and will add to its holdings of longer-term Treasury securities at a pace of $15 billion per month rather than $20 billion per month.
+ added: Beginning in October, the Committee will add to its holdings of agency mortgage-backed securities at a pace of $5 billion per month rather than $10 billion per month, and will add to its holdings of longer-term Treasury securities at a pace of $10 billion per month rather than $15 billion per month.
- removed: If incoming information broadly supports the Committee's expectation of ongoing improvement in labor market conditions and inflation moving back toward its longer-run objective, the Committee will likely reduce the pace of asset purchases in further measured steps at future meetings.
+ added: If incoming information broadly supports the Committee's expectation of ongoing improvement in labor market conditions and inflation moving back toward its longer-run objective, the Committee will end its current program of asset purchases at its next meeting.

## 28. 2014-12-17  (previous: 2014-10-29)

- removed: Information received since the Federal Open Market Committee met in September suggests that economic activity is expanding at a moderate pace.
- removed: Labor market conditions improved somewhat further, with solid job gains and a lower unemployment rate.
- removed: On balance, a range of labor market indicators suggests that underutilization of labor resources is gradually diminishing.
+ added: Information received since the Federal Open Market Committee met in October suggests that economic activity is expanding at a moderate pace.
+ added: Labor market conditions improved further, with solid job gains and a lower unemployment rate.
+ added: On balance, a range of labor market indicators suggests that underutilization of labor resources continues to diminish.
- removed: Inflation has continued to run below the Committee's longer-run objective.
- removed: Market-based measures of inflation compensation have declined somewhat; survey-based measures of longer-term inflation expectations have remained stable.
+ added: Inflation has continued to run below the Committee's longer-run objective, partly reflecting declines in energy prices.
+ added: Market-based measures of inflation compensation have declined somewhat further; survey-based measures of longer-term inflation expectations have remained stable.
- removed: The Committee expects that, with appropriate policy accommodation, economic activity will expand at a moderate pace, with labor market indicators and inflation moving toward levels the Committee judges consistent with its dual mandate.
+ added: The Committee expects that, with appropriate policy accommodation, economic activity will expand at a moderate pace, with labor market indicators moving toward levels the Committee judges consistent with its dual mandate.
- removed: Although inflation in the near term will likely be held down by lower energy prices and other factors, the Committee judges that the likelihood of inflation running persistently below 2 percent has diminished somewhat since early this year.
- removed: The Committee judges that there has been a substantial improvement in the outlook for the labor market since the inception of its current asset purchase program.
- removed: Moreover, the Committee continues to see sufficient underlying strength in the broader economy to support ongoing progress toward maximum employment in a context of price stability.
- removed: Accordingly, the Committee decided to conclude its asset purchase program this month.
- removed: The Committee is maintaining its existing policy of reinvesting principal payments from its holdings of agency debt and agency mortgage-backed securities in agency mortgage-backed securities and of rolling over maturing Treasury securities at auction.
- removed: This policy, by keeping the Committee's holdings of longer-term securities at sizable levels, should help maintain accommodative financial conditions.
+ added: The Committee expects inflation to rise gradually toward 2 percent as the labor market improves further and the transitory effects of lower energy prices and other factors dissipate.
+ added: The Committee continues to monitor inflation developments closely.
- removed: The Committee anticipates, based on its current assessment, that it likely will be appropriate to maintain the 0 to 1/4 percent target range for the federal funds rate for a considerable time following the end of its asset purchase program this month, especially if projected inflation continues to run below the Committee's 2 percent longer-run goal, and provided that longer-term inflation expectations remain well anchored.
+ added: Based on its current assessment, the Committee judges that it can be patient in beginning to normalize the stance of monetary policy.
+ added: The Committee sees this guidance as consistent with its previous statement that it likely will be appropriate to maintain the 0 to 1/4 percent target range for the federal funds rate for a considerable time following the end of its asset purchase program in October, especially if projected inflation continues to run below the Committee's 2 percent longer-run goal, and provided that longer-term inflation expectations remain well anchored.
+ added: The Committee is maintaining its existing policy of reinvesting principal payments from its holdings of agency debt and agency mortgage-backed securities in agency mortgage-backed securities and of rolling over maturing Treasury securities at auction.
+ added: This policy, by keeping the Committee's holdings of longer-term securities at sizable levels, should help maintain accommodative financial conditions.

## 29. 2017-11-01  (previous: 2017-09-20)

- removed: Information received since the Federal Open Market Committee met in July indicates that the labor market has continued to strengthen and that economic activity has been rising moderately so far this year.
- removed: Job gains have remained solid in recent months, and the unemployment rate has stayed low.
+ added: Information received since the Federal Open Market Committee met in September indicates that the labor market has continued to strengthen and that economic activity has been rising at a solid rate despite hurricane-related disruptions.
+ added: Although the hurricanes caused a drop in payroll employment in September, the unemployment rate declined further.
- removed: On a 12-month basis, overall inflation and the measure excluding food and energy prices have declined this year and are running below 2 percent.
+ added: Gasoline prices rose in the aftermath of the hurricanes, boosting overall inflation in September; however, inflation for items other than food and energy remained soft.
+ added: On a 12-month basis, both inflation measures have declined this year and are running below 2 percent.
- removed: Hurricanes Harvey, Irma, and Maria have devastated many communities, inflicting severe hardship.
- removed: Storm-related disruptions and rebuilding will affect economic activity in the near term, but past experience suggests that the storms are unlikely to materially alter the course of the national economy over the medium term.
+ added: Hurricane-related disruptions and rebuilding will continue to affect economic activity, employment, and inflation in the near term, but past experience suggests that the storms are unlikely to materially alter the course of the national economy over the medium term.
- removed: Higher prices for gasoline and some other items in the aftermath of the hurricanes will likely boost inflation temporarily; apart from that effect, inflation on a 12-month basis is expected to remain somewhat below 2 percent in the near term but to stabilize around the Committee's 2 percent objective over the medium term.
+ added: Inflation on a 12-month basis is expected to remain somewhat below 2 percent in the near term but to stabilize around the Committee's 2 percent objective over the medium term.
- removed: In October, the Committee will initiate the balance sheet normalization program described in the June 2017 Addendum to the Committee's Policy Normalization Principles and Plans.
+ added: The balance sheet normalization program initiated in October 2017 is proceeding.

## 30. 2018-05-02  (previous: 2018-03-21)

- removed: Information received since the Federal Open Market Committee met in January indicates that the labor market has continued to strengthen and that economic activity has been rising at a moderate rate.
- removed: Job gains have been strong in recent months, and the unemployment rate has stayed low.
- removed: Recent data suggest that growth rates of household spending and business fixed investment have moderated from their strong fourth-quarter readings.
- removed: On a 12-month basis, both overall inflation and inflation for items other than food and energy have continued to run below 2 percent.
- removed: Market-based measures of inflation compensation have increased in recent months but remain low; survey-based measures of longer-term inflation expectations are little changed, on balance.
+ added: Information received since the Federal Open Market Committee met in March indicates that the labor market has continued to strengthen and that economic activity has been rising at a moderate rate.
+ added: Job gains have been strong, on average, in recent months, and the unemployment rate has stayed low.
+ added: Recent data suggest that growth of household spending moderated from its strong fourth-quarter pace, while business fixed investment continued to grow strongly.
+ added: On a 12-month basis, both overall inflation and inflation for items other than food and energy have moved close to 2 percent.
+ added: Market-based measures of inflation compensation remain low; survey-based measures of longer-term inflation expectations are little changed, on balance.
- removed: The economic outlook has strengthened in recent months.
- removed: Inflation on a 12-month basis is expected to move up in coming months and to stabilize around the Committee's 2 percent objective over the medium term.
- removed: Near-term risks to the economic outlook appear roughly balanced, but the Committee is monitoring inflation developments closely.
- removed: In view of realized and expected labor market conditions and inflation, the Committee decided to raise the target range for the federal funds rate to 1-1/2 to 1-3/4 percent.
+ added: Inflation on a 12-month basis is expected to run near the Committee's symmetric 2 percent objective over the medium term.
+ added: Risks to the economic outlook appear roughly balanced.
+ added: In view of realized and expected labor market conditions and inflation, the Committee decided to maintain the target range for the federal funds rate at 1-1/2 to 1-3/4 percent.

## 31. 2018-08-01  (previous: 2018-06-13)

- removed: Information received since the Federal Open Market Committee met in May indicates that the labor market has continued to strengthen and that economic activity has been rising at a solid rate.
- removed: Job gains have been strong, on average, in recent months, and the unemployment rate has declined.
- removed: Recent data suggest that growth of household spending has picked up, while business fixed investment has continued to grow strongly.
- removed: On a 12-month basis, both overall inflation and inflation for items other than food and energy have moved close to 2 percent.
+ added: Information received since the Federal Open Market Committee met in June indicates that the labor market has continued to strengthen and that economic activity has been rising at a strong rate.
+ added: Job gains have been strong, on average, in recent months, and the unemployment rate has stayed low.
+ added: Household spending and business fixed investment have grown strongly.
+ added: On a 12-month basis, both overall inflation and inflation for items other than food and energy remain near 2 percent.
- removed: In view of realized and expected labor market conditions and inflation, the Committee decided to raise the target range for the federal funds rate to 1-3/4 to 2 percent.
+ added: In view of realized and expected labor market conditions and inflation, the Committee decided to maintain the target range for the federal funds rate at 1-3/4 to 2 percent.

## 32. 2018-11-08  (previous: 2018-09-26)

- removed: Information received since the Federal Open Market Committee met in August indicates that the labor market has continued to strengthen and that economic activity has been rising at a strong rate.
- removed: Job gains have been strong, on average, in recent months, and the unemployment rate has stayed low.
- removed: Household spending and business fixed investment have grown strongly.
+ added: Information received since the Federal Open Market Committee met in September indicates that the labor market has continued to strengthen and that economic activity has been rising at a strong rate.
+ added: Job gains have been strong, on average, in recent months, and the unemployment rate has declined.
+ added: Household spending has continued to grow strongly, while growth of business fixed investment has moderated from its rapid pace earlier in the year.
- removed: In view of realized and expected labor market conditions and inflation, the Committee decided to raise the target range for the federal funds rate to 2 to 2-1/4 percent.
+ added: In view of realized and expected labor market conditions and inflation, the Committee decided to maintain the target range for the federal funds rate at 2 to 2-1/4 percent.

## 33. 2019-05-01  (previous: 2019-03-20)

- removed: Information received since the Federal Open Market Committee met in January indicates that the labor market remains strong but that growth of economic activity has slowed from its solid rate in the fourth quarter.
- removed: Payroll employment was little changed in February, but job gains have been solid, on average, in recent months, and the unemployment rate has remained low.
- removed: Recent indicators point to slower growth of household spending and business fixed investment in the first quarter.
- removed: On a 12-month basis, overall inflation has declined, largely as a result of lower energy prices; inflation for items other than food and energy remains near 2 percent.
+ added: Information received since the Federal Open Market Committee met in March indicates that the labor market remains strong and that economic activity rose at a solid rate.
+ added: Job gains have been solid, on average, in recent months, and the unemployment rate has remained low.
+ added: Growth of household spending and business fixed investment slowed in the first quarter.
+ added: On a 12-month basis, overall inflation and inflation for items other than food and energy have declined and are running below 2 percent.

## 34. 2020-09-16  (previous: 2020-07-29)

- removed: The coronavirus outbreak is causing tremendous human and economic hardship across the United States and around the world.
- removed: Following sharp declines, economic activity and employment have picked up somewhat in recent months but remain well below their levels at the beginning of the year.
+ added: The COVID-19 pandemic is causing tremendous human and economic hardship across the United States and around the world.
+ added: Economic activity and employment have picked up in recent months but remain well below their levels at the beginning of the year.
- removed: The ongoing public health crisis will weigh heavily on economic activity, employment, and inflation in the near term, and poses considerable risks to the economic outlook over the medium term.
- removed: In light of these developments, the Committee decided to maintain the target range for the federal funds rate at 0 to 1/4 percent.
- removed: The Committee expects to maintain this target range until it is confident that the economy has weathered recent events and is on track to achieve its maximum employment and price stability goals.
- removed: The Committee will continue to monitor the implications of incoming information for the economic outlook, including information related to public health, as well as global developments and muted inflation pressures, and will use its tools and act as appropriate to support the economy.
- removed: In determining the timing and size of future adjustments to the stance of monetary policy, the Committee will assess realized and expected economic conditions relative to its maximum employment objective and its symmetric 2 percent inflation objective.
- removed: This assessment will take into account a wide range of information, including measures of labor market conditions, indicators of inflation pressures and inflation expectations, and readings on financial and international developments.
- removed: To support the flow of credit to households and businesses, over coming months the Federal Reserve will increase its holdings of Treasury securities and agency residential and commercial mortgage-backed securities at least at the current pace to sustain smooth market functioning, thereby fostering effective transmission of monetary policy to broader financial conditions.
- removed: In addition, the Open Market Desk will continue to offer large-scale overnight and term repurchase agreement operations.
- removed: The Committee will closely monitor developments and is prepared to adjust its plans as appropriate.
+ added: The ongoing public health crisis will continue to weigh on economic activity, employment, and inflation in the near term, and poses considerable risks to the economic outlook over the medium term.
+ added: The Committee seeks to achieve maximum employment and inflation at the rate of 2 percent over the longer run.
+ added: With inflation running persistently below this longer-run goal, the Committee will aim to achieve inflation moderately above 2 percent for some time so that inflation averages 2 percent over time and longer-term inflation expectations remain well anchored at 2 percent.
+ added: The Committee expects to maintain an accommodative stance of monetary policy until these outcomes are achieved.
+ added: The Committee decided to keep the target range for the federal funds rate at 0 to 1/4 percent and expects it will be appropriate to maintain this target range until labor market conditions have reached levels consistent with the Committee's assessments of maximum employment and inflation has risen to 2 percent and is on track to moderately exceed 2 percent for some time.
+ added: In addition, over coming months the Federal Reserve will increase its holdings of Treasury securities and agency mortgage-backed securities at least at the current pace to sustain smooth market functioning and help foster accommodative financial conditions, thereby supporting the flow of credit to households and businesses.
+ added: In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook.
+ added: The Committee would be prepared to adjust the stance of monetary policy as appropriate if risks emerge that could impede the attainment of the Committee's goals.
+ added: The Committee's assessments will take into account a wide range of information, including readings on public health, labor market conditions, inflation pressures and inflation expectations, and financial and international developments.

## 35. 2021-03-17  (previous: 2021-01-27)

- removed: The pace of the recovery in economic activity and employment has moderated in recent months, with weakness concentrated in the sectors most adversely affected by the pandemic.
- removed: Weaker demand and earlier declines in oil prices have been holding down consumer price inflation.
+ added: Following a moderation in the pace of the recovery, indicators of economic activity and employment have turned up recently, although the sectors most adversely affected by the pandemic remain weak.
+ added: Inflation continues to run below 2 percent.

## 36. 2021-04-28  (previous: 2021-03-17)

- removed: Following a moderation in the pace of the recovery, indicators of economic activity and employment have turned up recently, although the sectors most adversely affected by the pandemic remain weak.
- removed: Inflation continues to run below 2 percent.
+ added: Amid progress on vaccinations and strong policy support, indicators of economic activity and employment have strengthened.
+ added: The sectors most adversely affected by the pandemic remain weak but have shown improvement.
+ added: Inflation has risen, largely reflecting transitory factors.
- removed: The ongoing public health crisis continues to weigh on economic activity, employment, and inflation, and poses considerable risks to the economic outlook.
+ added: The ongoing public health crisis continues to weigh on the economy, and risks to the economic outlook remain.

## 37. 2021-06-16  (previous: 2021-04-28)

- removed: The COVID-19 pandemic is causing tremendous human and economic hardship across the United States and around the world.
- removed: Amid progress on vaccinations and strong policy support, indicators of economic activity and employment have strengthened.
+ added: Progress on vaccinations has reduced the spread of COVID-19 in the United States.
+ added: Amid this progress and strong policy support, indicators of economic activity and employment have strengthened.
- removed: The path of the economy will depend significantly on the course of the virus, including progress on vaccinations.
- removed: The ongoing public health crisis continues to weigh on the economy, and risks to the economic outlook remain.
+ added: The path of the economy will depend significantly on the course of the virus.
+ added: Progress on vaccinations will likely continue to reduce the effects of the public health crisis on the economy, but risks to the economic outlook remain.
- removed: With inflation running persistently below this longer-run goal, the Committee will aim to achieve inflation moderately above 2 percent for some time so that inflation averages 2 percent over time and longer‑term inflation expectations remain well anchored at 2 percent.
+ added: With inflation having run persistently below this longer-run goal, the Committee will aim to achieve inflation moderately above 2 percent for some time so that inflation averages 2 percent over time and longer‑term inflation expectations remain well anchored at 2 percent.

## 38. 2021-12-15  (previous: 2021-11-03)

- removed: The sectors most adversely affected by the pandemic have improved in recent months, but the summer's rise in COVID-19 cases has slowed their recovery.
- removed: Inflation is elevated, largely reflecting factors that are expected to be transitory.
- removed: Supply and demand imbalances related to the pandemic and the reopening of the economy have contributed to sizable price increases in some sectors.
+ added: The sectors most adversely affected by the pandemic have improved in recent months but continue to be affected by COVID-19.
+ added: Job gains have been solid in recent months, and the unemployment rate has declined substantially.
+ added: Supply and demand imbalances related to the pandemic and the reopening of the economy have continued to contribute to elevated levels of inflation.
- removed: Risks to the economic outlook remain.
+ added: Risks to the economic outlook remain, including from new variants of the virus.
- removed: With inflation having run persistently below this longer-run goal, the Committee will aim to achieve inflation moderately above 2 percent for some time so that inflation averages 2 percent over time and longer‑term inflation expectations remain well anchored at 2 percent.
- removed: The Committee expects to maintain an accommodative stance of monetary policy until these outcomes are achieved.
- removed: The Committee decided to keep the target range for the federal funds rate at 0 to 1/4 percent and expects it will be appropriate to maintain this target range until labor market conditions have reached levels consistent with the Committee's assessments of maximum employment and inflation has risen to 2 percent and is on track to moderately exceed 2 percent for some time.
- removed: In light of the substantial further progress the economy has made toward the Committee's goals since last December, the Committee decided to begin reducing the monthly pace of its net asset purchases by $10 billion for Treasury securities and $5 billion for agency mortgage-backed securities.
- removed: Beginning later this month, the Committee will increase its holdings of Treasury securities by at least $70 billion per month and of agency mortgage‑backed securities by at least $35 billion per month.
- removed: Beginning in December, the Committee will increase its holdings of Treasury securities by at least $60 billion per month and of agency mortgage-backed securities by at least $30 billion per month.
+ added: In support of these goals, the Committee decided to keep the target range for the federal funds rate at 0 to 1/4 percent.
+ added: With inflation having exceeded 2 percent for some time, the Committee expects it will be appropriate to maintain this target range until labor market conditions have reached levels consistent with the Committee's assessments of maximum employment.
+ added: In light of inflation developments and the further improvement in the labor market, the Committee decided to reduce the monthly pace of its net asset purchases by $20 billion for Treasury securities and $10 billion for agency mortgage-backed securities.
+ added: Beginning in January, the Committee will increase its holdings of Treasury securities by at least $40 billion per month and of agency mortgage‑backed securities by at least $20 billion per month.

## 39. 2023-06-14  (previous: 2023-05-03)

- removed: Economic activity expanded at a modest pace in the first quarter.
+ added: Recent indicators suggest that economic activity has continued to expand at a modest pace.
- removed: In support of these goals, the Committee decided to raise the target range for the federal funds rate to 5 to 5-1/4 percent.
- removed: The Committee will closely monitor incoming information and assess the implications for monetary policy.
- removed: In determining the extent to which additional policy firming may be appropriate to return inflation to 2 percent over time, the Committee will take into account the cumulative tightening of monetary policy, the lags with which monetary policy affects economic activity and inflation, and economic and financial developments.
+ added: In support of these goals, the Committee decided to maintain the target range for the federal funds rate at 5 to 5-1/4 percent.
+ added: Holding the target range steady at this meeting allows the Committee to assess additional information and its implications for monetary policy.
+ added: In determining the extent of additional policy firming that may be appropriate to return inflation to 2 percent over time, the Committee will take into account the cumulative tightening of monetary policy, the lags with which monetary policy affects economic activity and inflation, and economic and financial developments.

## 40. 2023-09-20  (previous: 2023-07-26)

- removed: Recent indicators suggest that economic activity has been expanding at a moderate pace.
- removed: Job gains have been robust in recent months, and the unemployment rate has remained low.
+ added: Recent indicators suggest that economic activity has been expanding at a solid pace.
+ added: Job gains have slowed in recent months but remain strong, and the unemployment rate has remained low.
- removed: In support of these goals, the Committee decided to raise the target range for the federal funds rate to 5-1/4 to 5-1/2 percent.
+ added: In support of these goals, the Committee decided to maintain the target range for the federal funds rate at 5-1/4 to 5-1/2 percent.
