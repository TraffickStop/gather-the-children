aws dynamodb scan   --table-name People-o5msg6ojb5ahrlj5gj2g2aphsi-dev \
                    --select ALL_ATTRIBUTES \
                    --page-size 500 \
                    --max-items 100000 \
                    --output json | jq -r '.Items' | jq -r '(.[0] | keys_unsorted) as $keys | $keys, map([.[ $keys[] ].S])[] | @csv' > export.my-table.csv