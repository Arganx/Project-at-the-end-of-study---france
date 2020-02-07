set height 0
set disassembly-flavor intel
echo kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
r test.sample
x/10 $eip
where
i r
echo kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
q
