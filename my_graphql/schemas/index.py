type_defs = """
        type Query {
                generate_css_behavior(css_file_paths: [String]!): valid_css_conbination_list_output!
        }

        type valid_css_conbination_list_output @key(fields: "valid_css_combinations_file_json") {
                css_behavior_file_json: String!
                valid_css_combinations_file_json: String!
                information: String!
        }
"""
